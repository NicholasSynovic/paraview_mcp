## 2026-06-03 Session Start

### Current Makefile State (13 lines, confirmed)
- Lines 1-5: `build:` target (4 recipe lines, tab-indented) — PRESERVE BYTE-IDENTICAL
- Line 6: blank line between targets
- Lines 7-13: `create-dev:` target (6 recipe lines: conda init, conda create --file, pre-commit install, pre-commit autoupdate, rm -rf .venv, uv sync)
- NO `.PHONY` declaration currently

### Key Conventions
- All recipe lines use TAB (ASCII 0x09) indentation — confirmed by visual inspection
- `build:` target body uses bare `uv` (no conda wrapping) — OUT OF SCOPE, do not touch
- Environment name: `paraview_mcp` (from environment.yaml line 1)
- `pre-commit` and `uv` are pinned inside the conda env pip section (lines 168-180)

### What Changes
- INSERT `.PHONY: build create-dev` + blank line at top (before build:)
- REPLACE `create-dev:` recipe body with exactly 4 lines (conda env update, conda run pre-commit install, rm -rf .venv, conda run uv sync)
- REMOVE: conda init, conda create --file, pre-commit autoupdate

### What Does NOT Change
- `build:` target body: byte-identical
- The blank line between `build:` and `create-dev:`
- Any other file
Appended on 2026-06-03: Updated Makefile with .PHONY and new create-dev recipe; dry-run succeeded; tabs present as ^I in evidence file.
# Makefile create-dev update - verification
Date: 2026-06-03T11:57:55-05:00

Grep checks: see .omo/evidence/task-2-grep-checks.txt
Build recipe diff: .omo/evidence/task-2-build-before.txt vs .omo/evidence/task-2-build-after.txt
Git diff saved: .omo/evidence/task-2-git-diff.txt

Assertions summary:
---
Diff assertions:
PASS: addition of .PHONY: build create-dev
FAIL: addition of conda env update --file environment.yaml --prune - missing expected line: +\tconda env update --file environment.yaml --prune
FAIL: addition of conda run -n paraview_mcp pre-commit install - missing expected line: +\tconda run -n paraview_mcp pre-commit install
FAIL: addition of conda run -n paraview_mcp uv sync - missing expected line: +\tconda run -n paraview_mcp uv sync
FAIL: removal of conda init - missing expected line: -\tconda init
FAIL: removal of conda create --file environment.yaml - missing expected line: -\tconda create --file environment.yaml
FAIL: removal of pre-commit autoupdate - missing expected line: -\tpre-commit autoupdate
PASS: no removal of uv build
PASS: no removal of uv pip install dist

Verification assertions (re-run):
Re-running diff assertions with literal tabs
FAIL: addition of .PHONY: build create-dev - missing expected addition line
Found similar lines:
6:+.PHONY: build create-dev
PASS: addition of conda env update --file environment.yaml --prune
PASS: addition of conda run -n paraview_mcp pre-commit install
PASS: addition of conda run -n paraview_mcp uv sync
FAIL: removal of conda init - missing expected removal line
Found similar lines:
FAIL: removal of conda create --file environment.yaml - missing expected removal line
Found similar lines:
PASS: removal of pre-commit autoupdate
PASS: no removal of uv build
PASS: no removal of uv pip install dist
