# AGENTS.md

ParaView MCP server: a FastMCP server that exposes `paraview.simple` operations as MCP tools so an LLM client (Claude Desktop, etc.) can drive a live ParaView session over `pvserver`.

## Layout (only the non-obvious bits)

- `paraview_mcp/main.py` — FastMCP entrypoint. Defines every `@mcp.tool()` and instantiates one module-level `ParaViewManager`. The `default_prompt` string in this file is a **behavioral contract sent to the LLM** ("one function per reply", color-map tips, etc.). Editing tool docstrings/wording changes model behavior.
- `paraview_mcp/paraview_manager.py` (~1500 lines) — single class wrapping `paraview.simple`. All ParaView state lives here; `main.py` is a thin tool shim.
- `paraview_mcp/__init__.py` — empty. The package uses absolute imports; run `pip install -e .` before importing.

No tests, no CI.

## Environment & quirks

- `paraview.simple` is **only available from a ParaView build** (conda-forge `paraview` or a system ParaView install). It cannot be pip-installed. `pip install -e .` alone gives you `mcp` + `httpx` but the server will fail to import on startup.
- Python version signals disagree — trust the runtime constraint, not the files:
  - `.python-version` → `3.14`
  - `.pre-commit-config.yaml` → `python3.13`
  - `README.md` → `conda create ... python=3.10`
  - **In practice the python version is dictated by whatever the conda `paraview` package supports** (typically 3.10/3.11). Use that env to actually run the server. Pre-commit can use a different interpreter.
- If ParaView is installed outside the active env, pass `--paraview_package_path /path/to/site-packages` and `main.py` will `sys.path.append` it before importing.
- Logs are written to `~/paraview_logs/paraview_mcp_external.log` (created on import of `main.py`). Don't expect logs in the repo.

## Running the server

```bash
# 1. start pvserver (separate terminal, conda env with paraview)
pvserver --multi-clients --server-port=11111

# 2. start ParaView GUI and File → Connect to that pvserver

# 3. start the MCP server (requires pip install -e . first)
paraview-mcp --server localhost --port 11111
# or with an external ParaView install:
paraview-mcp --paraview_package_path /opt/paraview/lib/python3.x/site-packages
```

The README uses `pvserver --multi-clients --server-port=11111` (correct — `pvserver` is a binary, not a Python script) and the `paraview-mcp` console script (hyphen form) as the canonical entrypoint.

### Running notes

`main.py` now uses `from paraview_mcp.paraview_manager import ParaViewManager` (absolute import). Consequences:

- `python paraview_mcp/main.py` **no longer works standalone** — it requires `pip install -e .` first so `paraview_mcp` is on `sys.path`.
- `python -m paraview_mcp.main` works after install.
- The canonical invocation is the console script: `paraview-mcp --server localhost --port 11111`.

## Build / dev tooling

`pyproject.toml` now exists at the repo root. `make build` (`uv build`) and `make create-dev` (`uv sync`) should work again. The canonical install command is:

```bash
pip install -e .
```

This registers the `paraview-mcp` console script.

## Lint / format / hooks

Pre-commit is the source of truth for style. Hooks: `ruff-format`, `ruff-check`, `isort`, `bandit`, plus stock `pre-commit-hooks`. Install + run:

```bash
pre-commit install
pre-commit run --all-files
```

No `ruff.toml`/`pyproject.toml` config — ruff and isort run with defaults. Match existing style: 4-space indent (`.editorconfig`), double quotes, type hints on public tool signatures.

Note: `paraview_manager.py` does `from paraview.simple import *`. Ruff/isort will not flag this; do not "fix" it — the module relies on the star import for dozens of ParaView symbols.

## Adding or changing MCP tools

- Every tool is `@mcp.tool()` in `main.py`, delegates to a `pv_manager.<method>()`, and returns a human-readable status string. Keep that contract.
- Methods on `ParaViewManager` consistently return `(success: bool, message: str, ...payload)`. Preserve this shape — tool functions destructure it.
- Tool docstrings are sent to the LLM and double as prompt guidance (see the `[Tips: ...]` blocks). Edit them deliberately, not cosmetically.
- For list/dict parameters, prefer the OpenAI-compatible variants already in the file (`list[dict[str, float]]` etc.) — there are commented-out older signatures kept for reference; do not delete them without asking.
- If you add a tool, also append it to `list_commands()` so the LLM can discover it.

## Git / branches

- Active branch is `dev`. Two remotes: `origin` (fork: `NicholasSynovic/paraview_mcp`), `upstream` (`llnl/paraview_mcp`).
- Upstream README warns the pvserver-sync feature is deprecated in recent ParaView; stability issues are expected and **not** your bug to fix.
