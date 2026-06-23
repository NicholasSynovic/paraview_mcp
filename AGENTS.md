# AGENTS.md

ParaView MCP server: a FastMCP server that exposes `paraview.simple` operations as MCP tools so an LLM client (Claude Desktop, OpenCode, etc.) can drive a live ParaView session over `pvserver`.

## Package layout (the non-obvious bits)

The package is a thin controller + a single shared engine. The MCP tools and the `ParaViewManager` each live in exactly one place; the `v1`/`v2` packages are thin transport shims around them. Do **not** look for tool definitions in `main.py` or in the version packages.

- `paraview_mcp/main.py` — thin controller for the `paraview-mcp` console script. Parses args, sets up logging, optionally `sys.path.append`s an external ParaView install, then calls the selected engine's `run()` (`paraview_mcp.v1.pv_mcp.run()` or `paraview_mcp.v2.pv_mcp.run()`). **Imports the engine lazily inside `main()`** because importing it pulls in `paraview.simple`.
- `paraview_mcp/cli.py` — argparse surface only (no ParaView import). Requires a `v1`/`v2` subcommand; shared flags live on the `pv_parent` parent parser, so `v1` and `v2` both inherit `--paraview-server`, `--paraview-port`, `--paraview-package-path`, and the screenshot flags (`--compress-screenshots/--no-compress-screenshots`, `--max-screenshot-width`, `--screenshot-quality`). `v2` additionally defines `--server`/`--port` for the MCP transport bind address.
- `paraview_mcp/logger.py` — `setup_logging()`; writes to `~/paraview_logs/paraview_mcp_external.log` (dir created on call). Idempotent.
- `paraview_mcp/tools.py` (~1110 lines) — **the single source for all `@mcp.tool()` definitions** (39 registered tools) plus the module-level `mcp = FastMCP(...)`, the `default_prompt`, the `pv_manager` module global, `set_pv_manager()`, and `list_commands()`. `pv_manager` is `None` at import; each engine's `run()` constructs a `ParaViewManager` (so it can apply CLI screenshot settings) and installs it via `set_pv_manager()` before serving. The `default_prompt` string is a **behavioral contract sent to the LLM** ("only call strictly necessary functions per reply", color-map tips). Editing tool docstrings/`default_prompt` changes model behavior.
- `paraview_mcp/manager.py` (~3090 lines) — single `ParaViewManager` class wrapping `paraview.simple`. All ParaView state lives here; `tools.py` is a thin tool shim over it. It does `from paraview.simple import *` at module top **plus** dozens of lazy `from paraview.simple import ...` inside methods — do **not** "fix" the star import; the module relies on it.
- `paraview_mcp/v1/pv_mcp.py` and `paraview_mcp/v2/pv_mcp.py` — **thin `run()` shims only**. Both `import mcp, set_pv_manager, logger` from `paraview_mcp.tools` and share the same `mcp` instance and tool set. They differ only in transport: v1 serves over **stdio** (`mcp.run()`), v2 serves over MCP **streamable-http** (`mcp.run(transport="streamable-http")`) and binds to the CLI's `--server`/`--port` (MCP transport address, distinct from `--paraview-*`). Because the tools are shared, **there is no longer a "mirror v1 into v2" step** — edit `tools.py` once.
- `paraview_mcp/v1/__init__.py` and `paraview_mcp/v2/__init__.py` re-export `ParaViewManager` from `paraview_mcp.manager`. `v2/__init__.py` also exposes the FastMCP display name as the `MCP_SERVER_NAME` constant (kept for backward compatibility) — do **not** override the module dunder `__name__` (it breaks `from paraview_mcp.v2 import <submodule>`).
- No tests, no CI (CONTRIBUTING.md mentions Travis but there is no CI config in the repo). `data/` holds a couple of demo datasets (`tooth_*.raw`, `wavelet_benchmark.vti`).

## Entrypoint: keep cli.py / main.py / README in sync

`cli.py`, `main.py`, and the README "Running"/integration sections must agree on the argument namespace (a past mismatch made `paraview-mcp v1` raise `AttributeError`). Current verified interface:

- Run with: `paraview-mcp v1 --paraview-server localhost --paraview-port 11111` (bare `paraview-mcp v1` works on defaults).
- `main.py` reads `args.paraview_server`, `args.paraview_port`, `args.paraview_package_path`, `args.compress_screenshots`, `args.max_screenshot_width`, `args.screenshot_quality` for v1; v2 additionally reads `args.server`/`args.port` (MCP transport bind address).
- v1 `run()` takes `server`/`port`; v2 `run()` takes `paraview_server`/`paraview_port`/`mcp_server`/`mcp_port`. If you add/rename a CLI flag, update `cli.py`, the relevant `pv_mcp.run()` signature, the `main.py` call, and every command/JSON snippet in `README.md` + `opencode-config.json` together. Verify with `python -c "from paraview_mcp.cli import parse_args; parse_args([...])"` (no ParaView needed).

## Environment & quirks

- `paraview.simple` is **only available from a ParaView build** (conda-forge `paraview` or a system ParaView install). It cannot be pip-installed. `pip install -e .` alone gives you `fastmcp` + `httpx` + `mcp[cli]` but the server fails to import at runtime.
- Python version signals disagree — trust the runtime constraint, not the files:
    - `.python-version` → `3.14`; `.pre-commit-config.yaml` → `python3.13`; `pyproject.toml` → `requires-python = ">=3.10"`; README → conda `python=3.10`.
    - **In practice the Python version is dictated by whatever the conda `paraview` package supports** (typically 3.10/3.11). Use that env to run the server; pre-commit may use a different interpreter.
- External ParaView: pass `--paraview-package-path /path/to/site-packages` (defined on the shared parent parser; appended to `sys.path` in `main.py` before the engine import).

## Running the server

Three steps, in order, each in its own terminal inside the activated conda env:

```bash
# 1. pvserver (binary from conda-forge::paraview, not a Python script)
pvserver --multi-clients --server-port=11111

# 2. ParaView GUI → File → Connect → localhost:11111

# 3. MCP server (canonical entrypoint is the hyphenated console script)
paraview-mcp v1 --paraview-server localhost --paraview-port 11111
# or the streamable-http engine:
paraview-mcp v2 --paraview-server localhost --paraview-port 11111 --server localhost --port 8080
# or, for an external ParaView install:
paraview-mcp v1 --paraview-package-path /opt/paraview/lib/python3.x/site-packages
```

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

- `pyproject.toml` has a `[tool.ruff]` config (line-length 80, `ignore = ["F403", "F405"]` for the load-bearing star import). The prettier hook needs `bun`/`bunx` on PATH.
- Match existing style: 4-space indent (`.editorconfig`), double quotes, type hints on public tool signatures.

## Adding or changing MCP tools

- Every tool is `@mcp.tool()` in `paraview_mcp/tools.py` (defined once, shared by both engines), delegates to a `pv_manager.<method>()`, and returns a human-readable status string. Keep that contract.
- Methods on `ParaViewManager` (`paraview_mcp/manager.py`) consistently return `(success: bool, message: str, ...payload)`. Preserve this shape — tool functions destructure it.
- Tool docstrings are sent to the LLM and double as prompt guidance (see the `[Tips: ...]` blocks). Edit them deliberately, not cosmetically.
- For list/dict parameters, prefer the OpenAI-compatible variants already in the file (`list[dict[str, float]]` etc.). Several older signatures and tools are kept commented-out (`# @mcp.tool()`) for reference — do not delete them without asking.
- `list_commands()` is **generated from the registered tools** (`mcp._tool_manager.list_tools()`), so adding a `@mcp.tool()` automatically lists it — no manual list to maintain. Still update the **MCP Tool Reference** table in `README.md`.

## Git / branches / PRs

- Active branch is `dev`. Two remotes: `origin` (fork: `NicholasSynovic/paraview_mcp`), `upstream` (`llnl/paraview_mcp`).
- CONTRIBUTING.md: branch off `main`, use a fork + PR, imperative commit messages (e.g., "Adds X").
- Upstream README warns the pvserver-sync feature is deprecated in recent ParaView; ParaView-GUI sync/stability issues are expected and **not** your bug to fix.
