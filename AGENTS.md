# AGENTS.md

ParaView MCP server: a FastMCP server that exposes `paraview.simple` operations as MCP tools so an LLM client (Claude Desktop, OpenCode, etc.) can drive a live ParaView session over `pvserver`.

## Package layout (the non-obvious bits)

The package is split into a thin controller + a versioned engine. Do not look for tools in `main.py`.

- `paraview_mcp/main.py` — thin controller for the `paraview-mcp` console script. Parses args, sets up logging, optionally `sys.path.append`s an external ParaView install, then calls `paraview_mcp.v1.pv_mcp.run()`. **Imports the server lazily inside `main()`** because importing it pulls in `paraview.simple`.
- `paraview_mcp/cli.py` — argparse surface only (no ParaView import).
- `paraview_mcp/logger.py` — `setup_logging()`; writes to `~/paraview_logs/paraview_mcp_external.log` (dir created on call). Idempotent.
- `paraview_mcp/v1/pv_mcp.py` (~1160 lines) — **all `@mcp.tool()` definitions** + the module-level `mcp = FastMCP(...)`, `pv_manager`, and `run(server, port)`. The `default_prompt` string here is a **behavioral contract sent to the LLM** ("one function per reply", color-map tips). Editing tool docstrings/`default_prompt` changes model behavior.
- `paraview_mcp/v1/paraview_manager.py` (~3000 lines) — single `ParaViewManager` class wrapping `paraview.simple`. All ParaView state lives here; `pv_mcp.py` is a thin tool shim.
- `paraview_mcp/v2/` — empty placeholder package (a `v2` subcommand exists in the CLI but has no engine yet).

No tests, no CI (CONTRIBUTING.md mentions Travis but there is no CI config in the repo).

## KNOWN BUG: CLI / main.py are out of sync

`cli.py` and `main.py` disagree on the argument namespace. Verify before trusting any run command:

- `cli.py` requires a subcommand (`v1` or `v2`) and produces `args.version`, `args.paraview_server`, `args.paraview_port` (v2 also adds `args.server`/`args.port`).
- `main.py` reads `args.paraview_package_path`, `args.server`, `args.port` — **none of which `cli.py` produces for `v1`**. So `paraview-mcp v1` currently raises `AttributeError`, and the README's `paraview-mcp --server localhost --port 11111` form no longer parses.

If you touch the entrypoint, reconcile these three (`cli.py`, `main.py`, README "Running" section) together. The README documents the _intended_ interface, not the current one.

## Environment & quirks

- `paraview.simple` is **only available from a ParaView build** (conda-forge `paraview` or a system ParaView install). It cannot be pip-installed. `pip install -e .` alone gives you `fastmcp` + `httpx` + `mcp[cli]` but the server fails to import at runtime.
- `paraview_manager.py` does `from paraview.simple import *` at module top **plus** dozens of lazy `from paraview.simple import ...` inside methods. Ruff/isort will not flag the star import — do not "fix" it; the module relies on it.
- Python version signals disagree — trust the runtime constraint, not the files:
    - `.python-version` → `3.14`; `.pre-commit-config.yaml` → `python3.13`; `pyproject.toml` → `requires-python = ">=3.10"`; README → conda `python=3.10`.
    - **In practice the Python version is dictated by whatever the conda `paraview` package supports** (typically 3.10/3.11). Use that env to run the server; pre-commit may use a different interpreter.
- External ParaView: pass `--paraview_package_path /path/to/site-packages` (note: see CLI bug above — this flag is referenced by `main.py` but not defined in `cli.py`).

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
