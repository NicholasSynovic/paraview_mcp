# AGENTS.md

ParaView MCP server: a FastMCP server that exposes `paraview.simple` operations as MCP tools so an LLM client (Claude Desktop, OpenCode, etc.) can drive a live ParaView session over `pvserver`.

## Package layout (the non-obvious bits)

The package is split into a thin controller + a versioned engine. Do not look for tools in `main.py`.

- `paraview_mcp/main.py` — thin controller for the `paraview-mcp` console script. Parses args, sets up logging, optionally `sys.path.append`s an external ParaView install, then calls `paraview_mcp.v1.pv_mcp.run()`. **Imports the engine lazily inside `main()`** because importing it pulls in `paraview.simple`.
- `paraview_mcp/cli.py` — argparse surface only (no ParaView import). Requires a `v1`/`v2` subcommand; shared flags live on the `pv_parent` parent parser, so `v1` and `v2` both inherit `--paraview-server`, `--paraview-port`, `--paraview-package-path`, and the screenshot flags (`--compress-screenshots/--no-compress-screenshots`, `--max-screenshot-width`, `--screenshot-quality`).
- `paraview_mcp/logger.py` — `setup_logging()`; writes to `~/paraview_logs/paraview_mcp_external.log` (dir created on call). Idempotent.
- `paraview_mcp/v1/pv_mcp.py` (~1160 lines) — **all `@mcp.tool()` definitions** (43 tools) + the module-level `mcp = FastMCP(...)` and `run(...)`. `pv_manager` is module-global but set to `None` at import; `run()` constructs the `ParaViewManager` (so it can apply CLI screenshot settings) and reassigns it via `global pv_manager`. The `default_prompt` string is a **behavioral contract sent to the LLM** ("only call strictly necessary functions per reply", color-map tips). Editing tool docstrings/`default_prompt` changes model behavior.
- `paraview_mcp/v1/paraview_manager.py` (~3090 lines) — single `ParaViewManager` class wrapping `paraview.simple`. All ParaView state lives here; `pv_mcp.py` is a thin tool shim.
- `paraview_mcp/v2/` — **near-identical copy of v1** (same 43 tools, its own `paraview_manager.py` + `pv_mcp.py` with `run()`) and **now wired in**: `main.py` dispatches the `v2` engine to `paraview_mcp.v2.pv_mcp.run(...)`. The difference from v1 is the transport: v2 serves over MCP **streamable-http** (`mcp.run(transport="streamable-http")`) and binds to the CLI's `--server`/`--port` (MCP transport, distinct from `--paraview-*`), whereas v1 uses stdio. The leftover `NotImplementedError` in `main.py` is now only a dead `else` branch (the CLI restricts `engine` to `v1`/`v2`). Edits to v1 must usually be mirrored into v2 to keep them from diverging. Note: `v2/__init__.py` exposes the FastMCP display name as the `MCP_SERVER_NAME` constant — do **not** override the module dunder `__name__` (it breaks `from paraview_mcp.v2 import <submodule>`).

No tests, no CI (CONTRIBUTING.md mentions Travis but there is no CI config in the repo).

## Entrypoint: keep cli.py / main.py / README in sync

`cli.py`, `main.py`, and the README "Running"/integration sections must agree on the argument namespace (a past mismatch made `paraview-mcp v1` raise `AttributeError`). Current verified interface:

- Run with: `paraview-mcp v1 --paraview-server localhost --paraview-port 11111` (bare `paraview-mcp v1` works on defaults).
- `main.py` reads `args.paraview_server`, `args.paraview_port`, `args.paraview_package_path`, `args.compress_screenshots`, `args.max_screenshot_width`, `args.screenshot_quality` — all produced by `cli.py`.
- If you add/rename a CLI flag, update `cli.py`, the `pv_mcp.run()` signature, the `main.py` call, and every command/JSON snippet in `README.md` + `opencode-config.json` together. Verify with `python -c "from paraview_mcp.cli import parse_args; parse_args([...])"` (no ParaView needed).

## Environment & quirks

- `paraview.simple` is **only available from a ParaView build** (conda-forge `paraview` or a system ParaView install). It cannot be pip-installed. `pip install -e .` alone gives you `fastmcp` + `httpx` + `mcp[cli]` but the server fails to import at runtime.
- `paraview_manager.py` does `from paraview.simple import *` at module top **plus** dozens of lazy `from paraview.simple import ...` inside methods. Ruff/isort will not flag the star import — do not "fix" it; the module relies on it.
- Python version signals disagree — trust the runtime constraint, not the files:
    - `.python-version` → `3.14`; `.pre-commit-config.yaml` → `python3.13`; `pyproject.toml` → `requires-python = ">=3.10"`; README → conda `python=3.10`.
    - **In practice the Python version is dictated by whatever the conda `paraview` package supports** (typically 3.10/3.11). Use that env to run the server; pre-commit may use a different interpreter.
- External ParaView: pass `--paraview-package-path /path/to/site-packages` (defined on the shared parent parser; appended to `sys.path` in `main.py` before the engine import).

## Build / dev tooling

- Install: `pip install -e .` (registers the `paraview-mcp` console script → `paraview_mcp.main:main`). Build backend is **hatchling**; wheel packages `paraview_mcp` only.
- `Makefile` targets (all assume a conda env named `paraview_mcp`):
    - `make create-dev` — `conda env update --file environment.yaml --prune`, `pre-commit install`, then `uv sync --group dev`.
    - `make build` — bumps version to the latest git tag, `uv build`, installs the sdist.
    - `make freeze` — regenerates `environment.yaml` (`conda env export | grep -v '^prefix:'`). After freeze, manually verify `channels:` includes `nodefaults` and the `pip:` section has **no** self-reference to `paraview-mcp`.
- `paraview` is intentionally **absent** from `pyproject.toml` (conda-only). Do not add it.

## Lint / format / hooks

Pre-commit is the source of truth for style. Hooks: stock `pre-commit-hooks`, `isort`, `ruff-format`, `ruff-check`, `bandit`, and a **local `prettier`** hook run via `bunx` over JS/TS/CSS/HTML/JSON/Markdown/YAML (4-space tabs, print-width 80). Install + run:

```bash
pre-commit install
pre-commit run --all-files
```

- No `ruff.toml` and no `[tool.ruff]` — ruff/isort run with defaults. `pyproject.toml` has `[tool.black] line-length = 80` but **black is not in the hook chain**; treat line-length 80 as the convention.
- Match existing style: 4-space indent (`.editorconfig`), double quotes, type hints on public tool signatures.
- The prettier hook needs `bun`/`bunx` on PATH.

## Adding or changing MCP tools

- Every tool is `@mcp.tool()` in `paraview_mcp/v1/pv_mcp.py`, delegates to a `pv_manager.<method>()`, and returns a human-readable status string. Keep that contract.
- Methods on `ParaViewManager` consistently return `(success: bool, message: str, ...payload)`. Preserve this shape — tool functions destructure it.
- Tool docstrings are sent to the LLM and double as prompt guidance (see the `[Tips: ...]` blocks). Edit them deliberately, not cosmetically.
- For list/dict parameters, prefer the OpenAI-compatible variants already in the file (`list[dict[str, float]]` etc.). Several older signatures and tools are kept commented-out (`# @mcp.tool()`) for reference — do not delete them without asking.
- If you add a tool, also append it to `list_commands()` so the LLM can discover it, and update the **MCP Tool Reference** table in `README.md`.

## Git / branches / PRs

- Active branch is `dev`. Two remotes: `origin` (fork: `NicholasSynovic/paraview_mcp`), `upstream` (`llnl/paraview_mcp`).
- CONTRIBUTING.md: branch off `main`, use a fork + PR, imperative commit messages (e.g., "Adds X").
- Upstream README warns the pvserver-sync feature is deprecated in recent ParaView; ParaView-GUI sync/stability issues are expected and **not** your bug to fix.
