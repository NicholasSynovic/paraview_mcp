# AGENTS.md

FastMCP server that exposes `paraview.simple` as MCP tools so an LLM client (Claude Desktop, OpenCode, etc.) can drive a live ParaView session over `pvserver`.

## Layout (only the non-obvious bits)

- `paraview_mcp/main.py` — FastMCP entrypoint. Defines every `@mcp.tool()` and instantiates one module-level `ParaViewManager`. The `default_prompt` string (line ~37) is a **behavioral contract sent to the LLM** ("one function per reply", color-map tips, etc.). Editing tool docstrings/wording changes model behavior.
- `paraview_mcp/paraview_manager.py` (~3100 lines) — single class wrapping `paraview.simple`. All ParaView state lives here; `main.py` is a thin tool shim. It does `from paraview.simple import *` — do **not** "fix" the star import; dozens of symbols depend on it.
- `paraview_mcp/__init__.py` re-exports `ParaViewManager` via relative import, but `main.py` itself uses a bare `from paraview_manager import ParaViewManager` (not `from .paraview_manager`). Works only because the package directory ends up on `sys.path` at runtime. Keep this in mind before "fixing" the import — past upstream merges have reverted such cleanups.
- No tests, no CI workflows. `data/` holds a couple of demo datasets (`tooth_*.raw`, `wavelet_benchmark.vti`).

## Environment & quirks

- `paraview.simple` is **only available from a ParaView build** (conda-forge `paraview` or a system ParaView install). It cannot be pip-installed and is intentionally absent from `pyproject.toml`. `pip install -e .` alone gives you `mcp` + `httpx` but the server will fail to import on startup.
- Python version signals disagree across files — there is no single source of truth, so trust the runtime:
    - `.python-version` → `3.14`
    - `.pre-commit-config.yaml` → `python3.13`
    - `pyproject.toml` → `>=3.10`
    - `environment.yaml` pins `paraview=5.13.3=py310...` → the conda env actually runs on Python 3.10
    - **In practice the runtime Python is whatever the conda `paraview` package supplies (3.10).** Pre-commit can use a different interpreter; do not "unify" these without testing.
- `environment.yaml` has a stale header comment referencing a sibling project (`chatvis.main`, `uv run`, "minimal env for `pvpython`"). Ignore that wording — for this repo the conda env is the runtime env, and the README's `conda activate paraview_mcp && pip install -e .` flow is correct.
- If ParaView is installed outside the active env, pass `--paraview_package_path /path/to/site-packages` and `main.py` will `sys.path.append` it before importing.
- Logs go to `~/paraview_logs/paraview_mcp_external.log` (directory created on import of `main.py`). Don't look in the repo.
- Screenshot behavior is tuned by env vars read in `main.py`: `PARAVIEW_COMPRESS_SCREENSHOTS`, `PARAVIEW_MAX_SCREENSHOT_WIDTH`, `PARAVIEW_SCREENSHOT_QUALITY`.

## Running the server

Three steps, in order, each in its own terminal inside the activated conda env:

```bash
# 1. pvserver (binary from conda-forge::paraview, not a Python script)
pvserver --multi-clients --server-port=11111

# 2. ParaView GUI → File → Connect → localhost:11111

# 3. MCP server (canonical entrypoint is the hyphenated console script)
paraview-mcp --server localhost --port 11111
# or, for an external ParaView install:
paraview-mcp --paraview_package_path /opt/paraview/lib/python3.x/site-packages
```

`python paraview_mcp/main.py` and `python -m paraview_mcp.main` are **not** reliable because of the bare `from paraview_manager` import; use the console script.

## Build / dev tooling

- `make create-dev` — recreates the conda env from `environment.yaml`, installs pre-commit hooks, and runs `uv sync --group dev` inside the env. This is the supported setup path for contributors.
- `make build` — wipes `dist/`, tags the version from the latest git tag (`uv version`), runs `uv build`, then `uv pip install dist/*.tar.gz`. Requires a git tag to exist.
- `make freeze` — regenerates `environment.yaml`. **Manually verify after**: (1) channels include `nodefaults`, (2) the `pip:` section does **not** contain a self-reference to `paraview-mcp`. The Makefile prints this reminder.
- `opencode-config.json` at the repo root is a ready-made OpenCode config that wires this server up; run with `OPENCODE_CONFIG=opencode-config.json opencode`.

## Lint / format / hooks

Pre-commit is the source of truth for style. Hooks: `ruff-format`, `ruff-check`, `isort`, `bandit`, prettier (via `bunx`, requires `bun`), plus stock `pre-commit-hooks`.

```bash
pre-commit install
pre-commit run --all-files
```

No `ruff.toml` or `[tool.ruff]` config — ruff and isort run with defaults. Match existing style: 4-space indent (`.editorconfig`), double quotes, type hints on public tool signatures. `black` is configured in `pyproject.toml` (line-length 80) but is not in the pre-commit chain — ruff-format wins.

## Adding or changing MCP tools

- Every tool is `@mcp.tool()` in `main.py`, delegates to a `pv_manager.<method>()`, and returns a human-readable status string. Keep that contract.
- `ParaViewManager` methods consistently return `(success: bool, message: str, ...payload)`. Preserve this shape — the tool wrappers destructure it.
- Tool docstrings are sent to the LLM and double as prompt guidance (see the `[Tips: ...]` blocks). Edit them deliberately, not cosmetically.
- For list/dict parameters, prefer the OpenAI-compatible variants already in the file (`list[dict[str, float]]` etc.). Commented-out older signatures are kept for reference — do not delete them without asking.
- If you add a tool, also append it to `list_commands()` so the LLM can discover it. Note: `list_commands()` is already partially out of sync with the actual `@mcp.tool()` set — fix entries you touch but don't treat it as authoritative.

## Git / branches

- Two remotes: `origin` (fork: `NicholasSynovic/paraview_mcp`), `upstream` (`llnl/paraview_mcp`). Active development happens on `dev`; `main` tracks `origin/main`.
- Upstream README warns the pvserver-sync feature is deprecated in recent ParaView; GUI may show blank/incorrect content and stability issues are expected — **not your bug to fix**.
