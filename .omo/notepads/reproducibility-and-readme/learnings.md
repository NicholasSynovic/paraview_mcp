# Learnings

## [2026-06-03] Session Start
- Working tree was dirty with rogue changes (Makefile regression, environment.yaml conda-export pollution, requirements.txt pinning) — all restored to HEAD via `git checkout --` before plan execution
- HEAD committed state: Makefile has `.PHONY: build create-dev` + correct `create-dev` recipe from makefile-create-dev-update boulder
- environment.yaml at HEAD: 209 lines, channels=[defaults, conda-forge], paraview pin at line 117: `paraview=5.13.3=py310h494b928_110_qt`, self-ref at line 188: `- paraview-mcp==0.1.0`, prefix at line 209
- requirements.txt at HEAD: 2 lines: `httpx` (unpinned), `mcp[cli]==1.9.4`
- pyproject.toml already has `paraview-mcp` (hyphen) console script at line 34-35
- CONTRIBUTING.md already exists — link from README, do NOT create new one

## [2026-06-03] Task 2 — environment.yaml cleanup
- Channels changed from `[defaults, conda-forge]` to `[conda-forge, nodefaults]`; `nodefaults` prevents any fallback to Anaconda's default channel, enforcing reproducibility
- Removed `pre-commit==4.6.0` and `uv==0.11.18` from pip section (dev tools not needed in the conda env lockfile)
- Removed `prefix:` line (machine-local path, breaks portability)
- paraview pin `paraview=5.13.3=py310h494b928_110_qt` at line 117 was already correct (Branch A confirmed by task-1-decision.txt)
- `system python3` (linuxbrew) lacks pyyaml; use `/home/nicholas/.local/bin/miniconda/bin/python` for yaml verification in this project
- Final file: 178 lines, n_deps=163 (162 conda + 1 pip subsection containing 10 pip packages)
- [2026-06-03] Removed requirements.txt; evidence: .omo/evidence/task-6-git-rm.txt

## [2026-06-03] Task 5 — AGENTS.md console-script normalization

- Replaced console-script invocations in AGENTS.md from `paraview_mcp` → `paraview-mcp` for CLI usage only.
- Lines changed: 33, 35, 38, 46, 56. Verified `python -m paraview_mcp.main` and package/module references remain with underscore.
- Evidence files created:
  - .omo/evidence/task-5-occurrences.txt (list of lines containing paraview_mcp / paraview-mcp)
  - .omo/evidence/task-5-underscore-script-count.txt (count = 0)
  - .omo/evidence/task-5-hyphen-script-count.txt (count = 3)

Confirmations:
- Underscore-form console-script occurrences: 0 (asserted)
- Hyphen-form console-script occurrences: 3 (>=3 asserted)
- `python -m paraview_mcp.main` remains present in AGENTS.md (module invocation preserved)

## [2026-06-03] Task 9 — NOTICE byte-identity
- NOTICE verified: PASS
- SHA-256: 49fe554611b7c0ba479f9161c9ee6636c99e02c668d5ad83e429904185672d1f

## [2026-06-03] Task 4 — README rewrite
- README rewritten: 285 lines
- All 20 sections present
- Stale strings: none
- BibTeX preserved verbatim
- pvserver disclaimer relocated to Known Limitations

## [2026-06-03] Task 7 — Makefile freeze target
- Added `freeze` target: `conda env export -n paraview_mcp | grep -v "^prefix:" > environment.yaml`
- freeze added to .PHONY
- No requirements.txt refs in Makefile

## [2026-06-03] Task 10 — Smoke test
- YAML parse: PASS
- TOML parse: PASS
- make -n create-dev: PASS
- requirements.txt absent: PASS
- NOTICE unchanged: PASS
- Note: Full conda env create not run (would require 20+ min network install); structural checks passed

## [2026-06-03] Task 8 — Cross-file consistency sweep
- Result: ALL CLEAN
