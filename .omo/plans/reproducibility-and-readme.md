# Reproducibility Cleanup + README Rewrite

## TL;DR

> **Quick Summary**: Clean up the conda environment for reproducibility on linux-64 (drop user-specific `prefix:`, drop circular self-reference, switch to `conda-forge` + `nodefaults` channels with a verify-first pin strategy), consolidate dev dependencies into `pyproject.toml` `[dependency-groups]`, delete `requirements.txt`, standardize the console script name to `paraview-mcp` (hyphen), and fully rewrite `README.md` with executive summary, MCP intro, mermaid architecture diagram, OpenCode + Claude Code integration sections, tool reference, ToC, troubleshooting, badges, and a maintenance section that documents the new `make freeze` workflow. NOTICE file stays verbatim.
>
> **Deliverables**:
>
> - Cleaned `environment.yaml` (verified pins, no prefix, no self-ref, channels=conda-forge+nodefaults, no dev tools in pip section)
> - Updated `pyproject.toml` with `[dependency-groups] dev = [...]`
> - Updated `Makefile` (new `freeze` target, updated `create-dev` that no longer reads `requirements.txt`, hyphenated script references)
> - Deleted `requirements.txt`
> - Updated `AGENTS.md` (hyphenated `paraview-mcp` references, any README-driven stale-instruction fixes)
> - Fully rewritten `README.md` (new structure, MCP intro, integrations, diagram, ToC, troubleshooting, badges, maintenance section)
> - `NOTICE` left byte-identical (legal compliance)
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves (1 verification + 1 file-rewrite + 1 cross-file consistency + 1 final review)
> **Critical Path**: Task 1 (conda-forge verification) -> Task 2 (environment.yaml rewrite) -> Task 10 (full conda env QA install) -> F1-F4

---

## Context

### Original Request

User asked to (1) improve conda environment reproducibility - knowing that `paraview==5.13.3` forces conda and cannot be pulled from PyPI - and (2) rewrite the `README.md` with an executive summary, MCP intro, build/install/run section, OpenCode integration (https://opencode.ai/docs/mcp-servers/), Claude Code integration (https://code.claude.com/docs/en/mcp), and other clarity improvements. User cannot make git commits during agent sessions (GPG blocker).

### Interview Summary

**Key Discussions**:

- **Conda lock strategy**: User initially open to `conda-lock`, then withdrew after Metis surfaced the bootstrap chicken-and-egg + maintenance cost. Final approach: single full-pinned `environment.yaml`, no separate lock file.
- **NOTICE file**: After Metis flagged the LLNL Apache-2.0 / BSD-3 attribution requirement, user chose to keep `NOTICE` verbatim and reference it from README. Original "inline + delete" plan was abandoned.
- **Channel migration**: User accepted the "verify-first" approach - confirm `paraview=5.13.3` is on conda-forge before committing to `channels: [conda-forge, nodefaults]`. Plan branches based on whether the exact build hash is available.
- **Console script name**: User chose hyphenated `paraview-mcp` as canonical (per PEP 503 / packaging convention). `pyproject.toml` already has this; README/AGENTS.md/Makefile need updates.
- **Reproducibility target**: linux-64 only.
- **README additions**: All six selected - ToC, mermaid diagram, troubleshooting, tool reference, contributing pointer, shields.io badges.

**Research Findings**:

- Current `environment.yaml` is 209 lines, fully pinned with build hashes - good starting point, but has 3 reproducibility bugs (user-specific `prefix:` line 209, circular `paraview-mcp==0.1.0` self-reference line 188, `defaults` channel listed first).
- `pyproject.toml` already declares `paraview-mcp` script with hyphen at line 34. Module name uses underscore (`paraview_mcp.main:main`). Both forms work on CLI due to pip normalization, but hyphen is canonical.
- `requirements.txt` duplicates `pyproject.toml` runtime deps and adds `uv` + `pre-commit` - this is the wrong place for dev tools.
- `README.md` has 3 stale items: `python pvserver` (line 43-47 - pvserver is a binary), Claude config uses `paraview_mcp` underscore (line 33-38), `git clone https://github.com/LLNL/...` (line 17-19 - should be NicholasSynovic/paraview_mcp).
- `Makefile` `create-dev` target does `conda env update --prune` + `pip install -r requirements.txt` + `pre-commit install`.

### Metis Review

**Identified Gaps** (all addressed):

- NOTICE legal preservation requirement -> kept verbatim, scope updated
- conda-forge availability risk for exact build hash -> verify-first task added as Wave 1
- conda-lock bootstrap complexity -> dropped entirely
- Console script name inconsistency between files -> standardized on hyphen, in-scope expanded
- `make freeze` command form ambiguity (`--no-builds` vs with builds) -> resolved to WITH builds (consistent with full-pin strategy)

### Oracle Phase 1 Non-Blocking Observations (executor should heed)

- The draft preserves historical statements in `Original Request` and `Current State Findings` that mention NOTICE inline/delete. These are historical; ONLY the FINAL Scope Boundaries and FINAL Verification Strategy in the draft (and this plan) are authoritative.
- `uv sync --group dev` behavior: if uv creates a project-local `.venv` instead of installing into the active conda env, switch to `uv pip install --group dev` or the uv equivalent that respects the active interpreter. Do NOT change the plan's intent - only the command form.
- `CONTRIBUTING.md` already exists in the repo. README should link to it. Do NOT create a new one.

---

## Work Objectives

### Core Objective

Make the project's conda environment reproducible on linux-64 without third-party lock tooling, consolidate dev dependencies into `pyproject.toml`, standardize the console-script name to `paraview-mcp`, and rewrite `README.md` to be a self-contained onboarding document.

### Concrete Deliverables

- `environment.yaml` - cleaned and verified, single source of truth for the conda env
- `pyproject.toml` - extended with `[dependency-groups] dev`
- `Makefile` - new `freeze` target, updated `create-dev`, hyphenated script references
- `requirements.txt` - DELETED
- `AGENTS.md` - hyphenated `paraview-mcp` references
- `README.md` - fully rewritten per the structure defined below
- `NOTICE` - UNCHANGED (legal compliance, byte-identical before/after)

### Definition of Done

- [ ] `python -c "import yaml; yaml.safe_load(open('environment.yaml'))"` exits 0
- [ ] `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` exits 0
- [ ] `make -n create-dev` (dry-run) prints commands with no errors
- [ ] `conda env create -f environment.yaml -n paraview_mcp_qa` succeeds end-to-end
- [ ] `which paraview-mcp` returns a path inside the QA env
- [ ] `python -c "import paraview.simple"` exits 0 inside the QA env
- [ ] `uv sync --group dev` (or uv equivalent inside conda env) installs `pre-commit` and `uv` per pyproject dependency-group
- [ ] `git diff NOTICE` returns empty (file unchanged)
- [ ] `requirements.txt` does not exist
- [ ] `grep -r "python pvserver" README.md` returns empty
- [ ] `grep -r "paraview_mcp" README.md AGENTS.md Makefile` returns ONLY package-name / module-path usages, NO console-script references
- [ ] `grep "LLNL/paraview_mcp" README.md` returns empty
- [ ] All README ToC anchors resolve to real sections
- [ ] Mermaid block in README parses without error
- [ ] QA env torn down: `conda env remove -n paraview_mcp_qa -y`

### Must Have

- Verify `paraview=5.13.3` availability on conda-forge BEFORE committing to `nodefaults`
- Full-pin `environment.yaml` with build hashes where conda-forge supports them
- Hyphenated `paraview-mcp` as canonical console-script name in all docs
- `NOTICE` file preserved verbatim
- README includes: ToC, executive summary, MCP intro, mermaid architecture diagram, install/run, OpenCode config, Claude Code config, tool reference, troubleshooting/FAQ, maintenance section (with `make freeze`), known limitations (pvserver deprecation), contributing pointer, citation, authors, license, shields.io badges, NOTICE reference
- Clean `conda env create` from a fresh prefix works on linux-64

### Must NOT Have (Guardrails)

- NO changes to `paraview_mcp/*.py`
- NO changes to `.pre-commit-config.yaml`
- NO `conda-lock`, `conda-lock.yml`, `make lock` target, or any conda-lock bootstrap anywhere (README, pyproject, Makefile, AGENTS.md)
- NO modification, deletion, or inlining of `NOTICE`
- NO git commits, no `git config` changes, no `--no-verify` hook bypass
- NO creation of new files outside the deliverable list (no new CONTRIBUTING.md, no LICENSE rewrite, no new lockfiles)
- NO `defaults` channel anywhere in `environment.yaml`
- NO silent fallback if `paraview=5.13.3` is missing from conda-forge - escalate to user
- NO scope creep: do NOT add CI workflows, do NOT add Dockerfile, do NOT add multi-platform support
- NO removal of the pvserver-deprecation disclaimer (it must remain, but move to "Known Limitations" near bottom)
- NO `python pvserver` (stale) references in any rewritten content
- NO `paraview_mcp` (underscore) console-script references in README, AGENTS.md, or Makefile
- NO `git clone https://github.com/LLNL/...` in README

### Spec Framework Integration

- **Detected Framework**: None
- **Rationale**: No `openspec/`, `.specify/`, or `_bmad/` directories exist in this repo. Standard plan format applies.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision

- **Infrastructure exists**: NO unit-test framework in this project (project is a thin MCP shim, no `tests/` dir)
- **Automated tests**: NONE (this plan touches only docs + config files; no Python code changes)
- **Framework**: N/A
- **Compensating verification**: Three-layer agent QA (static / install / doc-sanity) below

### QA Policy

Every task MUST include agent-executed QA scenarios using these tools:

- **Config files (YAML/TOML/Makefile)**: `Bash` running `python -c`, `make -n`, parser commands
- **README rewrite**: `Bash` for grep-based stale-string checks, `webfetch` or `curl -I` for URL liveness, `look_at` for mermaid render check
- **Full env install**: `Bash` running `conda env create`, `which`, `python -c "import ..."` commands
- Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`

### Three QA Layers (referenced by tasks)

- **Layer 1 (static)**: YAML/TOML parse, `make -n`, NOTICE-unchanged check, markdown stale-string grep - fast, runs in every relevant task
- **Layer 2 (install)**: `conda env create` -> activate -> `pip install -e .` -> `uv sync --group dev` -> `which paraview-mcp` -> `import paraview.simple` -> teardown (5-15 min, runs in the integration wave only)
- **Layer 3 (doc sanity)**: ToC anchor check, mermaid parse, URL liveness, stale-string greps for `python pvserver` / underscore script / LLNL clone URL (runs in the README task and the final review wave)

---

## Execution Strategy

### Parallel Execution Waves

> 4 waves. Wave 1 = verify-first (1 task, blocks downstream channel decisions). Wave 2 = parallel file rewrites (5 tasks, maximum parallelism). Wave 3 = cross-file consistency + integration QA (3 tasks). Wave FINAL = 4 parallel reviewers.

```
Wave 1 (Start Immediately - verification gate):
└── Task 1: Verify paraview=5.13.3 availability on conda-forge [quick]

Wave 2 (After Wave 1 - parallel file work, MAX PARALLEL):
├── Task 2: Clean and rewrite environment.yaml (depends: 1) [unspecified-high]
├── Task 3: Add [dependency-groups] dev to pyproject.toml [quick]
├── Task 4: Rewrite README.md with new structure [writing]
├── Task 5: Update AGENTS.md hyphenated script references [quick]
└── Task 6: Delete requirements.txt [quick]

Wave 3 (After Wave 2 - integration + Makefile + QA):
├── Task 7: Update Makefile (add freeze target, drop requirements.txt, hyphenate) (depends: 3, 6) [quick]
├── Task 8: Cross-file consistency sweep (script name + repo URL + stale commands) (depends: 2, 4, 5, 7) [quick]
└── Task 9: NOTICE byte-identity verification (depends: 4) [quick]

Wave 4 (After Wave 3 - the long install QA):
└── Task 10: Full conda env install + smoke test (depends: 2, 3, 6, 7) [unspecified-high]

Wave FINAL (After ALL tasks - 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code/config quality review (unspecified-high)
├── Task F3: Real manual QA on rewritten README (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 -> Task 2 -> Task 10 -> F1-F4 -> user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Wave 2)
```

### Dependency Matrix

- **Task 1**: depends on - / blocks 2
- **Task 2**: depends on 1 / blocks 7, 8, 10
- **Task 3**: depends on - / blocks 7, 10
- **Task 4**: depends on - / blocks 8, 9
- **Task 5**: depends on - / blocks 8
- **Task 6**: depends on - / blocks 7, 10
- **Task 7**: depends on 3, 6 / blocks 8, 10
- **Task 8**: depends on 2, 4, 5, 7 / blocks F1-F4
- **Task 9**: depends on 4 / blocks F1-F4
- **Task 10**: depends on 2, 3, 6, 7 / blocks F1-F4
- **F1-F4**: depend on 1-10 / blocks user okay

### Agent Dispatch Summary

- **Wave 1**: 1 task - T1 -> `quick`
- **Wave 2**: 5 tasks - T2 -> `unspecified-high`, T3 -> `quick`, T4 -> `writing`, T5 -> `quick`, T6 -> `quick`
- **Wave 3**: 3 tasks - T7 -> `quick`, T8 -> `quick`, T9 -> `quick`
- **Wave 4**: 1 task - T10 -> `unspecified-high`
- **FINAL**: 4 tasks - F1 -> `oracle`, F2 -> `unspecified-high`, F3 -> `unspecified-high`, F4 -> `deep`

---

## TODOs

- [x]   1. Verify `paraview=5.13.3` availability on conda-forge

    **What to do**:
    - Activate or create a temporary conda env with only the `conda` client (use base env if available)
    - Run: `conda search -c conda-forge --override-channels 'paraview=5.13.3' --info` and capture full output
    - Parse output to determine which branch applies:
        - **Branch A (exact build hash present)**: The build `py310h494b928_110_qt` (from current environment.yaml line 117) is listed on conda-forge -> Task 2 uses exact build hash pin `paraview=5.13.3=py310h494b928_110_qt`
        - **Branch B (version present, different build)**: `paraview=5.13.3` exists but only with a different build hash -> Task 2 uses version pin only `paraview=5.13.3` and accepts the conda-forge build hash output by the solver
        - **Branch C (version absent)**: `paraview=5.13.3` is not on conda-forge at all -> HALT plan, escalate to user, do NOT proceed to Task 2
    - Save the full `conda search` output as evidence
    - Write a one-line decision file `.omo/evidence/task-1-decision.txt` containing one of `BRANCH_A:<build_hash>`, `BRANCH_B`, or `BRANCH_C:HALT`

    **Must NOT do**:
    - Do NOT run `conda install`, `conda env create`, or any state-changing command in this task
    - Do NOT silently fall through to `defaults` channel if conda-forge lacks the package
    - Do NOT proceed to Task 2 if Branch C - escalate first

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Single deterministic `conda search` invocation + branch decision write; no design judgment needed.
    - **Skills**: none
        - Reason: No domain-specific skill overlaps a `conda search` call.
    - **Skills Evaluated but Omitted**:
        - `customize-opencode`: not opencode config work

    **Parallelization**:
    - **Can Run In Parallel**: NO (it is the sole Wave 1 gate)
    - **Parallel Group**: Wave 1 (alone)
    - **Blocks**: Task 2
    - **Blocked By**: None (can start immediately)

    **References**:

    **Pattern References**:
    - `environment.yaml:117` - Current paraview pin `paraview=5.13.3=py310h494b928_110_qt`; this is the build hash to check for on conda-forge
    - `environment.yaml:1-7` - Current channel list (`defaults`, `conda-forge`); shows the migration target

    **External References**:
    - conda-forge package search: `https://anaconda.org/conda-forge/paraview` - Cross-reference if `conda search` output is ambiguous
    - conda docs on `--override-channels`: `https://docs.conda.io/projects/conda/en/latest/commands/search.html` - Why `--override-channels` is required to test conda-forge in isolation

    **WHY Each Reference Matters**:
    - `environment.yaml:117` tells the executor the EXACT build hash to look for in conda-forge output - without it, "exact match" is ambiguous
    - `--override-channels` flag is mandatory; without it the user's configured channels leak into the search and Branch A/B detection becomes unreliable

    **Acceptance Criteria**:
    - [ ] `.omo/evidence/task-1-conda-search.txt` exists and contains the full `conda search` output
    - [ ] `.omo/evidence/task-1-decision.txt` exists and contains exactly one of `BRANCH_A:<hash>`, `BRANCH_B`, or `BRANCH_C:HALT`
    - [ ] If Branch C: a user-facing message is posted explaining the halt; Task 2 is NOT started

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: conda-forge has paraview=5.13.3 (Branch A or B)
      Tool: Bash
      Preconditions: conda CLI is on PATH; network access available
      Steps:
        1. Run: conda search -c conda-forge --override-channels 'paraview=5.13.3' --info > .omo/evidence/task-1-conda-search.txt 2>&1
        2. Run: grep -c "^paraview " .omo/evidence/task-1-conda-search.txt
        3. If count > 0, grep for the exact build string `py310h494b928_110_qt` in the output; write BRANCH_A:py310h494b928_110_qt or BRANCH_B to the decision file
      Expected Result: decision file contains BRANCH_A:<hash> or BRANCH_B; conda-search output file is non-empty
      Failure Indicators: search file empty, network error, decision file missing
      Evidence: .omo/evidence/task-1-conda-search.txt, .omo/evidence/task-1-decision.txt

    Scenario: conda-forge does NOT have paraview=5.13.3 (Branch C - HALT)
      Tool: Bash
      Preconditions: `conda search` ran and returned no matching packages
      Steps:
        1. Confirm: grep -c "^paraview " .omo/evidence/task-1-conda-search.txt returns 0
        2. Write BRANCH_C:HALT to .omo/evidence/task-1-decision.txt
        3. Post user-facing message: "Halt: paraview=5.13.3 not found on conda-forge. Decision needed before proceeding."
      Expected Result: decision file contains BRANCH_C:HALT; plan execution stops; no other tasks start
      Evidence: .omo/evidence/task-1-decision.txt, message visible in orchestrator log
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-1-conda-search.txt`
    - [ ] `.omo/evidence/task-1-decision.txt`

    **Commit**: NO (user defers all commits)

- [x]   2. Clean and rewrite `environment.yaml`

    **What to do**:
    - Read Task 1's `.omo/evidence/task-1-decision.txt` and select the paraview pin form accordingly (Branch A: exact build; Branch B: version-only)
    - Open `environment.yaml` and produce a cleaned version with:
        - Line 1: `name: paraview_mcp` (unchanged)
        - Channels block: `channels:` then `  - conda-forge` then `  - nodefaults` (ONLY these two; remove `defaults`)
        - Dependencies block: keep all existing pinned conda dependencies with build hashes (the file is already build-pinned), in the same order, EXCEPT replace the `paraview=...` line per Task 1's decision
        - `pip:` sub-block: KEEP only the runtime deps that are NOT in `pyproject.toml [dependency-groups] dev` (i.e., keep `httpx==0.28.1` and `mcp[cli]==1.9.4` if present); REMOVE the circular `paraview-mcp==0.1.0` self-reference at line 188; REMOVE `uv==0.11.18` and `pre-commit==4.6.0` (those move to dev group)
        - Remove the trailing `prefix:` line entirely (currently line 209)
    - Save the cleaned file in place
    - Run `python -c "import yaml; d=yaml.safe_load(open('environment.yaml')); print(d['channels']); print(len(d['dependencies']))"` to confirm structure

    **Must NOT do**:
    - Do NOT change conda dependency versions or build hashes (other than paraview, per Task 1)
    - Do NOT add new packages
    - Do NOT add `defaults` channel
    - Do NOT preserve `prefix:` line
    - Do NOT keep `paraview-mcp==0.1.0` self-reference under `pip:`
    - Do NOT keep `uv` or `pre-commit` in the pip section

    **Recommended Agent Profile**:
    - **Category**: `unspecified-high`
        - Reason: Touches a single 209-line YAML file with multiple coordinated edits (channels, paraview pin from decision file, pip section pruning, prefix removal). Requires careful before/after verification.
    - **Skills**: none
        - Reason: No skill specifically targets conda environment.yaml editing.

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Tasks 3, 4, 5, 6 in Wave 2)
    - **Parallel Group**: Wave 2
    - **Blocks**: Tasks 7, 8, 10
    - **Blocked By**: Task 1

    **References**:

    **Pattern References**:
    - `environment.yaml:1-7` - Current header (name + channels) - this is what gets rewritten
    - `environment.yaml:117` - Current paraview pin; replace per Task 1 decision file
    - `environment.yaml:188` - Circular self-reference `paraview-mcp==0.1.0` under pip; DELETE this line
    - `environment.yaml:209` - Hardcoded `prefix: /home/...`; DELETE this line
    - `.omo/evidence/task-1-decision.txt` (from Task 1) - Tells you whether to use exact build hash or version-only pin

    **API/Type References**:
    - PyYAML safe_load semantics: empty `prefix:` removal must preserve trailing newline on the file (POSIX text file convention)

    **External References**:
    - conda channel priority docs: `https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/channels.html` - `nodefaults` semantics
    - Reproducible conda envs: `https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment` - Why `prefix:` is user-specific and harmful

    **WHY Each Reference Matters**:
    - `environment.yaml:188` is the bug that makes the file un-rebuildable (pip tries to install the package being built); deletion is non-obvious without this pointer
    - `environment.yaml:209` `prefix:` looks harmless but is per-user and breaks reproducibility on other machines

    **Acceptance Criteria**:
    - [ ] `python -c "import yaml; d=yaml.safe_load(open('environment.yaml'))"` exits 0
    - [ ] `python -c "import yaml; d=yaml.safe_load(open('environment.yaml')); assert d['channels']==['conda-forge','nodefaults']"` exits 0
    - [ ] `! grep -n "^prefix:" environment.yaml`
    - [ ] `! grep -n "paraview-mcp==0.1.0" environment.yaml`
    - [ ] `! grep -n "uv==" environment.yaml`
    - [ ] `! grep -n "pre-commit==" environment.yaml`
    - [ ] paraview line matches the form dictated by `.omo/evidence/task-1-decision.txt`
    - [ ] `git diff --stat environment.yaml` shows changes ONLY to this file

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: Cleaned environment.yaml parses and has correct channels
      Tool: Bash
      Preconditions: Task 1 completed; decision file present
      Steps:
        1. Run: python -c "import yaml; d=yaml.safe_load(open('environment.yaml')); print('channels:', d['channels']); print('n_deps:', len(d.get('dependencies', [])))" > .omo/evidence/task-2-yaml-parse.txt 2>&1
        2. Assert: grep -q "channels: \['conda-forge', 'nodefaults'\]" .omo/evidence/task-2-yaml-parse.txt
        3. Assert: ! grep -n "^prefix:" environment.yaml
        4. Assert: ! grep -nE "paraview-mcp==0\.1\.0|^\s*-\s*uv==|^\s*-\s*pre-commit==" environment.yaml
      Expected Result: All assertions pass; YAML parses successfully; channels are exactly ['conda-forge','nodefaults']
      Failure Indicators: yaml.YAMLError thrown, channels contains 'defaults', prefix: still present, self-reference still present
      Evidence: .omo/evidence/task-2-yaml-parse.txt

    Scenario: paraview pin matches Task 1 decision
      Tool: Bash
      Preconditions: .omo/evidence/task-1-decision.txt exists and starts with BRANCH_A or BRANCH_B
      Steps:
        1. Read first line of decision file
        2. If BRANCH_A:<hash>: assert `grep -n "paraview=5.13.3=$hash" environment.yaml` returns exactly 1 line
        3. If BRANCH_B: assert `grep -nE "paraview=5\.13\.3($|[^=])" environment.yaml` returns exactly 1 line and `grep -n "paraview=5.13.3=" environment.yaml` returns 0 lines
      Expected Result: paraview pin form matches the decision exactly
      Evidence: .omo/evidence/task-2-paraview-pin-check.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-2-yaml-parse.txt`
    - [ ] `.omo/evidence/task-2-paraview-pin-check.txt`

    **Commit**: NO (user defers all commits)

- [x]   3. Add `[dependency-groups] dev` to `pyproject.toml`

    **What to do**:
    - Open `pyproject.toml`. Confirm current state: script entry at lines 34-35 (`paraview-mcp = "paraview_mcp.main:main"`); no existing `[dependency-groups]` table.
    - Append (or insert in logical position) a new TOML table:
        ```toml
        [dependency-groups]
        dev = [
            "pre-commit==4.6.0",
            "uv==0.11.18",
            "ruff",
        ]
        ```
    - Pin versions match those previously in `requirements.txt` (pre-commit==4.6.0, uv==0.11.18). `ruff` is unpinned because `.pre-commit-config.yaml` controls its version during hook runs.
    - Preserve all existing fields, comments, and ordering. Only ADD the new table.
    - Run `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['dependency-groups']['dev'])"` to verify

    **Must NOT do**:
    - Do NOT remove or rename any existing key
    - Do NOT change the script entry `paraview-mcp = "paraview_mcp.main:main"` at lines 34-35
    - Do NOT add runtime deps to the dev group (httpx, mcp[cli] stay in the main dependencies / conda env)
    - Do NOT add a `[tool.uv]` section unless absolutely required by `uv sync --group dev` (defer to Task 7's QA - only add if Task 10 install fails without it)

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Pure additive TOML edit; no design decisions.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Tasks 2, 4, 5, 6 in Wave 2)
    - **Parallel Group**: Wave 2
    - **Blocks**: Tasks 7, 10
    - **Blocked By**: None

    **References**:

    **Pattern References**:
    - `pyproject.toml` (full file, 45 lines) - Read first to identify insertion point and preserve formatting
    - `pyproject.toml:34-35` - Existing script entry; DO NOT TOUCH
    - `requirements.txt` (4 lines) - Source of truth for dev tool versions: pre-commit==4.6.0, uv==0.11.18

    **External References**:
    - PEP 735 dependency groups: `https://peps.python.org/pep-0735/` - Official spec for `[dependency-groups]` table
    - uv dependency-groups docs: `https://docs.astral.sh/uv/concepts/dependencies/#dependency-groups` - How `uv sync --group dev` resolves it

    **WHY Each Reference Matters**:
    - PEP 735 confirms the syntax `[dependency-groups]\ndev = [...]` is the canonical form and not a uv-specific extension; the project remains tool-agnostic
    - requirements.txt versions are the source of truth - copying them prevents accidental drift

    **Acceptance Criteria**:
    - [ ] `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert 'dev' in d['dependency-groups']"` exits 0
    - [ ] `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert 'pre-commit==4.6.0' in d['dependency-groups']['dev']"` exits 0
    - [ ] `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert 'uv==0.11.18' in d['dependency-groups']['dev']"` exits 0
    - [ ] `grep -n 'paraview-mcp = "paraview_mcp.main:main"' pyproject.toml` returns exactly 1 line (unchanged)
    - [ ] `git diff --stat pyproject.toml` shows changes ONLY to this file

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: pyproject.toml parses and dev group is correct
      Tool: Bash
      Preconditions: requirements.txt still exists (it will be deleted in Task 6)
      Steps:
        1. Run: python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); import json; print(json.dumps(d.get('dependency-groups',{}), indent=2))" > .omo/evidence/task-3-toml-parse.txt 2>&1
        2. Assert: grep -q '"pre-commit==4.6.0"' .omo/evidence/task-3-toml-parse.txt
        3. Assert: grep -q '"uv==0.11.18"' .omo/evidence/task-3-toml-parse.txt
        4. Assert: grep -q '"ruff"' .omo/evidence/task-3-toml-parse.txt
      Expected Result: dev group contains exactly the three expected deps with correct pins
      Failure Indicators: tomllib.TOMLDecodeError, dev key missing, version mismatch with requirements.txt
      Evidence: .omo/evidence/task-3-toml-parse.txt

    Scenario: Existing script entry preserved
      Tool: Bash
      Preconditions: Edit complete
      Steps:
        1. Run: grep -nE '^paraview-mcp\s*=\s*"paraview_mcp\.main:main"$' pyproject.toml > .omo/evidence/task-3-script-preserved.txt
        2. Assert: file is non-empty (exactly 1 match)
      Expected Result: Script entry at lines 34-35 unchanged
      Evidence: .omo/evidence/task-3-script-preserved.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-3-toml-parse.txt`
    - [ ] `.omo/evidence/task-3-script-preserved.txt`

    **Commit**: NO (user defers all commits)

- [x]   4. Rewrite `README.md` with new structure

    **What to do**:
    - Read current `README.md` (76 lines) for context only; the rewrite REPLACES it entirely
    - Produce a new README with this section order:
        1. **H1 title** + shields.io badges (Python version supported by paraview conda pkg, License Apache-2.0, MCP protocol)
        2. **Executive Summary** (3-5 sentences: what this is, who it's for, what it lets an LLM client do)
        3. **Table of Contents** (auto-anchor links to every H2 below)
        4. **What is MCP?** (2-3 sentence intro + link to https://modelcontextprotocol.io/)
        5. **Architecture** (mermaid diagram showing: LLM Client -> MCP server (paraview-mcp) -> pvserver -> ParaView GUI; brief caption)
        6. **Prerequisites** (conda with `paraview` package available, `pvserver` binary, linux-64)
        7. **Installation** (`conda env create -f environment.yaml -n paraview_mcp`, `conda activate paraview_mcp`, `pip install -e .`, `uv sync --group dev` for contributors)
        8. **Running** (start pvserver, connect ParaView GUI, start MCP server with `paraview-mcp --server localhost --port 11111`)
        9. **Integration: OpenCode** (JSON config snippet for OpenCode `~/.config/opencode/opencode.json` per https://opencode.ai/docs/mcp-servers/)
        10. **Integration: Claude Code** (JSON config snippet per https://code.claude.com/docs/en/mcp; use `paraview-mcp` hyphen form)
        11. **Integration: Claude Desktop** (keep existing JSON snippet but fix to hyphen form)
        12. **MCP Tool Reference** (hand-list every `@mcp.tool()` from `paraview_mcp/main.py` with one-line description; group by category: connection, sources, filters, color/visualization, camera, export, utility)
        13. **Maintenance** (`make freeze` regenerates pins after env mutation; explain the post-export manual steps: re-add `nodefaults`, remove pip self-reference)
        14. **Troubleshooting / FAQ** (top 5 issues: pvserver version mismatch, missing paraview module, ConnectionRefused, hung session, log file location at `~/paraview_logs/paraview_mcp_external.log`)
        15. **Known Limitations** (pvserver-sync deprecation disclaimer - moved from old README top)
        16. **Contributing** (link to existing `CONTRIBUTING.md`)
        17. **Citation** (preserve existing BibTeX entry if present in old README; otherwise add placeholder linking to NicholasSynovic/paraview_mcp)
        18. **Authors** (original LLNL authors + current maintainer)
        19. **License** (Apache-2.0, link to LICENSE)
        20. **Notice** (one sentence: "Third-party attributions are recorded in [NOTICE](./NOTICE).")
    - Stale-string requirements (the rewrite MUST NOT introduce these):
        - NO `python pvserver` (pvserver is a binary)
        - NO `paraview_mcp` underscore in console-script position (always `paraview-mcp`)
        - NO `git clone https://github.com/LLNL/paraview_mcp.git` (use `https://github.com/NicholasSynovic/paraview_mcp.git`)
        - NO `paraview_mcp_server.py` filename (old name; canonical entrypoint is `paraview-mcp` console script)
        - NO mention of conda-lock anywhere
    - Tone: technical, no marketing fluff, no emoji except in section headers if helpful for scanning

    **Must NOT do**:
    - Do NOT modify any file other than `README.md`
    - Do NOT delete or modify `NOTICE`
    - Do NOT create a new `CONTRIBUTING.md` (link to existing one)
    - Do NOT add a Dockerfile reference or CI badges for workflows that don't exist
    - Do NOT promise multi-platform support (linux-64 only)
    - Do NOT remove the pvserver-deprecation disclaimer; relocate it to Known Limitations

    **Recommended Agent Profile**:
    - **Category**: `writing`
        - Reason: Long-form documentation rewrite requiring narrative cohesion, technical accuracy, and tone control across ~20 sections.
    - **Skills**: none from available list directly target README authoring
        - Reason: `customize-opencode` is opencode-specific (not project READMEs); `security-research` is unrelated.

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Tasks 2, 3, 5, 6 in Wave 2)
    - **Parallel Group**: Wave 2
    - **Blocks**: Tasks 8, 9
    - **Blocked By**: None

    **References**:

    **Pattern References**:
    - `README.md` (current, 76 lines) - Read for context: existing badges, citation, authors, disclaimer text to preserve/relocate
    - `AGENTS.md` (lines 30-44) - Authoritative "Running the server" section; the README must agree with this
    - `AGENTS.md` (lines 50-55) - Notes on `pip install -e .` requirement; replicate in Installation section
    - `paraview_mcp/main.py` - Source of truth for every `@mcp.tool()` definition; iterate to build the Tool Reference section
    - `pyproject.toml:34-35` - Confirms canonical script name is `paraview-mcp`
    - `NOTICE` - File to REFERENCE (do not inline)
    - `CONTRIBUTING.md` (if exists at repo root) - Link target for Contributing section
    - `LICENSE` - Link target for License section

    **API/Type References**:
    - MCP server tool docstrings inside `paraview_mcp/main.py` are themselves prompt-tuning; preserve their summaries verbatim in the Tool Reference

    **External References**:
    - MCP spec: `https://modelcontextprotocol.io/` - Link target for "What is MCP?"
    - OpenCode MCP docs: `https://opencode.ai/docs/mcp-servers/` - Authoritative JSON config schema for OpenCode integration
    - Claude Code MCP docs: `https://code.claude.com/docs/en/mcp` - Authoritative JSON config schema for Claude Code integration
    - shields.io: `https://shields.io/` - Badge URL generator
    - mermaid live editor: `https://mermaid.live/` - Verify the architecture diagram parses
    - Conda channel priority docs: `https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/channels.html` - Background for Maintenance section explanation of `nodefaults`

    **WHY Each Reference Matters**:
    - `paraview_mcp/main.py` is the ONLY source of truth for the tool list; do not invent or omit tools
    - `AGENTS.md:30-44` is the most accurate Run section in the repo today; the README's Running section must not diverge
    - `pyproject.toml:34-35` is the ONLY source of truth for the console-script name; deviating creates the very bug this plan fixes

    **Acceptance Criteria**:
    - [ ] `README.md` exists and has > 200 lines (rough size sanity)
    - [ ] All 20 sections from "What to do" are present (grep `^## ` returns at least 18 H2 sections, plus H1 + ToC)
    - [ ] `! grep -n "python pvserver" README.md`
    - [ ] `! grep -nE "paraview_mcp\s+--server" README.md` (no underscore script form)
    - [ ] `! grep -n "LLNL/paraview_mcp" README.md`
    - [ ] `! grep -n "paraview_mcp_server\.py" README.md`
    - [ ] `! grep -n "conda-lock" README.md`
    - [ ] `grep -n "paraview-mcp" README.md` returns >= 3 lines (hyphen form used)
    - [ ] `grep -n "```mermaid" README.md` returns exactly 1 line
    - [ ] `grep -n "NicholasSynovic/paraview_mcp" README.md` returns >= 1 line
    - [ ] `grep -n "NOTICE" README.md` returns >= 1 line (reference exists)
    - [ ] `grep -n "make freeze" README.md` returns >= 1 line (maintenance section)
    - [ ] `grep -n "opencode.ai/docs/mcp-servers" README.md` returns >= 1 line
    - [ ] `grep -n "code.claude.com/docs/en/mcp" README.md` returns >= 1 line

    **QA Scenarios (MANDATORY)**:

    ````
    Scenario: README structural completeness
      Tool: Bash
      Preconditions: README.md has been rewritten
      Steps:
        1. Run: grep -nE "^#{1,2} " README.md > .omo/evidence/task-4-headings.txt
        2. Assert: line count of .omo/evidence/task-4-headings.txt >= 19 (1 H1 + ToC + 17+ H2)
        3. Run: for h2 in "Executive Summary" "Table of Contents" "What is MCP" "Architecture" "Prerequisites" "Installation" "Running" "OpenCode" "Claude Code" "MCP Tool Reference" "Maintenance" "Troubleshooting" "Known Limitations" "Contributing" "License"; do grep -q "$h2" README.md || echo "MISSING: $h2"; done > .omo/evidence/task-4-section-check.txt
        4. Assert: .omo/evidence/task-4-section-check.txt is empty (no MISSING lines)
      Expected Result: All required H2 sections present
      Failure Indicators: any MISSING line in check file, heading count too low
      Evidence: .omo/evidence/task-4-headings.txt, .omo/evidence/task-4-section-check.txt

    Scenario: Stale-string greps all return empty
      Tool: Bash
      Steps:
        1. For each forbidden pattern run grep; concatenate results
        2. Run: { grep -n "python pvserver" README.md; grep -nE "paraview_mcp\s+--server" README.md; grep -n "LLNL/paraview_mcp" README.md; grep -n "paraview_mcp_server\.py" README.md; grep -n "conda-lock" README.md; } > .omo/evidence/task-4-stale-strings.txt 2>&1
        3. Assert: .omo/evidence/task-4-stale-strings.txt is empty
      Expected Result: Empty file (no stale strings)
      Evidence: .omo/evidence/task-4-stale-strings.txt

    Scenario: Mermaid block parses
      Tool: Bash + look_at
      Steps:
        1. Extract the mermaid block between ```mermaid and ``` to .omo/evidence/task-4-mermaid.mmd
        2. Use `look_at` (or webfetch to mermaid.live render endpoint) to validate the syntax
      Expected Result: Mermaid block parses without syntax error; diagram shows LLM Client -> paraview-mcp -> pvserver -> ParaView nodes
      Evidence: .omo/evidence/task-4-mermaid.mmd, .omo/evidence/task-4-mermaid-render.png (if look_at produces one)

    Scenario: Integration JSON snippets are valid JSON
      Tool: Bash
      Steps:
        1. Extract OpenCode JSON snippet to .omo/evidence/task-4-opencode.json
        2. Extract Claude Code JSON snippet to .omo/evidence/task-4-claude-code.json
        3. Extract Claude Desktop JSON snippet to .omo/evidence/task-4-claude-desktop.json
        4. For each: python -c "import json,sys; json.load(open(sys.argv[1]))" <path>
      Expected Result: All three JSON snippets parse without error
      Failure Indicators: json.JSONDecodeError
      Evidence: three .json files + parse exit codes
    ````

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-4-headings.txt`
    - [ ] `.omo/evidence/task-4-section-check.txt`
    - [ ] `.omo/evidence/task-4-stale-strings.txt`
    - [ ] `.omo/evidence/task-4-mermaid.mmd`
    - [ ] `.omo/evidence/task-4-opencode.json`, `.omo/evidence/task-4-claude-code.json`, `.omo/evidence/task-4-claude-desktop.json`

    **Commit**: NO (user defers all commits)

- [x]   5. Update `AGENTS.md` to hyphenated `paraview-mcp` script references

    **What to do**:
    - Open `AGENTS.md`. Search for all occurrences of `paraview_mcp` used as a CONSOLE-SCRIPT name (e.g., in bash code blocks where it follows `$` or is the command being invoked).
    - Replace those occurrences with `paraview-mcp` (hyphen).
    - DO NOT touch occurrences of `paraview_mcp` used as:
        - Python package name (`paraview_mcp/main.py`, `from paraview_mcp.paraview_manager ...`)
        - Module path (`paraview_mcp.main:main`)
        - Directory name (`paraview_mcp/`)
        - Log filename (`paraview_mcp_external.log`)
    - Specifically, lines 35 and 38 of current `AGENTS.md` contain `paraview_mcp --server` and `paraview_mcp` console-script invocations - these are the targets.
    - Also: line 56 example `python -m paraview_mcp.main` is a module invocation, NOT a console-script - keep as is.
    - Run a grep diff before/after to confirm

    **Must NOT do**:
    - Do NOT modify any other file
    - Do NOT change package/module references (only console-script invocations)
    - Do NOT add or remove sections

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Surgical text replacement; <5 lines changed in a single file.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Tasks 2, 3, 4, 6 in Wave 2)
    - **Parallel Group**: Wave 2
    - **Blocks**: Task 8
    - **Blocked By**: None

    **References**:

    **Pattern References**:
    - `AGENTS.md:35` - `paraview_mcp --server localhost --port 11111` -> change to `paraview-mcp --server localhost --port 11111`
    - `AGENTS.md:38` - `paraview_mcp --paraview_package_path ...` -> change to `paraview-mcp --paraview_package_path ...` (note: only the leading command changes; `--paraview_package_path` flag name uses underscore and is unchanged)
    - `AGENTS.md:53` - `paraview_mcp` console script reference in "Running notes" -> change to `paraview-mcp`
    - `AGENTS.md:55` - `python -m paraview_mcp.main` - DO NOT change (module form)
    - `AGENTS.md:56` - `paraview_mcp --server localhost --port 11111` in canonical-invocation note -> change to `paraview-mcp ...`
    - `pyproject.toml:34-35` - Authoritative source of hyphen form

    **WHY Each Reference Matters**:
    - The distinction between console-script (hyphen) and module/package (underscore) is subtle but critical; lines 55-56 of AGENTS.md contain BOTH forms back-to-back, and only one should change

    **Acceptance Criteria**:
    - [ ] `grep -nE "paraview-mcp\s+--server" AGENTS.md` returns >= 2 lines
    - [ ] `grep -nE "paraview-mcp\s+--paraview_package_path" AGENTS.md` returns >= 1 line
    - [ ] `grep -nE "^\s*paraview_mcp\s+--" AGENTS.md` returns 0 lines (no console-script form with underscore remains)
    - [ ] `grep -n "python -m paraview_mcp.main" AGENTS.md` returns 1 line (module form preserved)
    - [ ] `grep -n "paraview_mcp/main.py" AGENTS.md` returns >= 1 line (path form preserved)
    - [ ] `git diff --stat AGENTS.md` shows changes ONLY to this file

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: Console-script references hyphenated, module/package references preserved
      Tool: Bash
      Steps:
        1. Run: grep -nE "paraview[_-]mcp" AGENTS.md > .omo/evidence/task-5-occurrences.txt
        2. Run: grep -cE "^\s*paraview_mcp\s+--" AGENTS.md > .omo/evidence/task-5-underscore-script-count.txt
        3. Assert: cat .omo/evidence/task-5-underscore-script-count.txt prints 0
        4. Run: grep -cE "paraview-mcp\s+--" AGENTS.md > .omo/evidence/task-5-hyphen-script-count.txt
        5. Assert: integer value >= 3
        6. Assert: grep -q "python -m paraview_mcp.main" AGENTS.md (module form preserved)
        7. Assert: grep -q "paraview_mcp/main.py" AGENTS.md (path form preserved)
      Expected Result: Zero underscore-form console-script invocations; >=3 hyphen-form invocations; module/path references intact
      Evidence: .omo/evidence/task-5-occurrences.txt, .omo/evidence/task-5-underscore-script-count.txt, .omo/evidence/task-5-hyphen-script-count.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-5-occurrences.txt`
    - [ ] `.omo/evidence/task-5-underscore-script-count.txt`
    - [ ] `.omo/evidence/task-5-hyphen-script-count.txt`

    **Commit**: NO (user defers all commits)

- [x]   6. Delete `requirements.txt`

    **What to do**:
    - Run `git rm requirements.txt` (preserves git history; the file enters the staged-for-deletion state but no commit is run per the commit guardrail)
    - Confirm `requirements.txt` no longer exists at repo root
    - Capture before/after evidence

    **Must NOT do**:
    - Do NOT commit the deletion (user defers commits)
    - Do NOT use `rm` instead of `git rm` (we want git to track the deletion)
    - Do NOT delete any other file

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Single `git rm` invocation.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Tasks 2, 3, 4, 5 in Wave 2)
    - **Parallel Group**: Wave 2
    - **Blocks**: Tasks 7, 10
    - **Blocked By**: None (but logically depends on Task 3 having staged its dev-group additions; in practice both can run independently)

    **References**:

    **Pattern References**:
    - `requirements.txt` (4 lines: httpx==0.28.1, mcp[cli]==1.9.4, uv==0.11.18, pre-commit==4.6.0) - File being deleted; capture its contents to evidence first for audit
    - `pyproject.toml` (after Task 3) - The new `[dependency-groups] dev` table absorbs uv + pre-commit; httpx and mcp[cli] remain conda env deps

    **WHY Each Reference Matters**:
    - Capturing the deleted file's contents to evidence proves nothing was lost (every dep has a new home in either pyproject or environment.yaml)

    **Acceptance Criteria**:
    - [ ] `test ! -f requirements.txt` exits 0
    - [ ] `git status --short requirements.txt` shows `D  requirements.txt` (staged deletion)
    - [ ] `.omo/evidence/task-6-requirements-snapshot.txt` contains the original 4-line file contents

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: requirements.txt is removed and tracked as deleted
      Tool: Bash
      Preconditions: requirements.txt exists at repo root
      Steps:
        1. Run: cp requirements.txt .omo/evidence/task-6-requirements-snapshot.txt
        2. Run: git rm requirements.txt
        3. Assert: test ! -f requirements.txt
        4. Run: git status --short requirements.txt > .omo/evidence/task-6-git-status.txt
        5. Assert: grep -qE "^D\s+requirements\.txt" .omo/evidence/task-6-git-status.txt
      Expected Result: File gone from working tree; staged for deletion in git; snapshot preserved in evidence
      Failure Indicators: file still present, git status shows untracked instead of deleted, snapshot missing
      Evidence: .omo/evidence/task-6-requirements-snapshot.txt, .omo/evidence/task-6-git-status.txt

    Scenario: No other file accidentally deleted
      Tool: Bash
      Steps:
        1. Run: git status --short > .omo/evidence/task-6-full-status.txt
        2. Run: grep -cE "^\sD\s|^D\s" .omo/evidence/task-6-full-status.txt
        3. Assert: count == 1 (only requirements.txt staged for deletion)
      Expected Result: Exactly one deletion in staged area
      Evidence: .omo/evidence/task-6-full-status.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-6-requirements-snapshot.txt`
    - [ ] `.omo/evidence/task-6-git-status.txt`
    - [ ] `.omo/evidence/task-6-full-status.txt`

    **Commit**: NO (user defers all commits)

- [x]   7. Update `Makefile`: add `freeze` target, drop `requirements.txt` from `create-dev`, hyphenate script references

    **What to do**:
    - Open `Makefile` (12 lines currently). Identify the `create-dev` target.
    - **Change 1 - `create-dev` target**: Remove the `pip install -r requirements.txt` line. Add `uv sync --group dev` in its place (or, if `uv sync` does not respect the active conda env, use `uv pip install --group dev`). The `conda env update --prune` and `pre-commit install` lines stay.
    - **Change 2 - add `freeze` target**:
        ```makefile
        .PHONY: freeze
        freeze:
        	conda env export -n paraview_mcp | grep -v "^prefix:" > environment.yaml
        	@echo "NOTE: After freeze, manually verify channels include 'nodefaults' and pip section does not contain 'paraview-mcp'."
        ```
    - **Change 3 - script-name references**: If any Makefile target invokes `paraview_mcp` as a console script (e.g., `run:` target), change to `paraview-mcp`. Current Makefile may not have such a target; if not, this change is a no-op.
    - Run `make -n create-dev` and `make -n freeze` to confirm both dry-runs succeed

    **Must NOT do**:
    - Do NOT add a `lock` target or any conda-lock-related target
    - Do NOT remove the `build` or any other existing target
    - Do NOT change indentation style (Makefile requires TABs, not spaces - this is non-negotiable)
    - Do NOT add `paraview-mcp` as a runtime target unless it already existed under another name

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Small surgical Makefile edits (2-3 changes in a 12-line file).
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: NO (depends on Tasks 3 and 6 - the dev-group must exist in pyproject and requirements.txt must be gone before `create-dev` can be safely rewritten)
    - **Parallel Group**: Wave 3
    - **Blocks**: Tasks 8, 10
    - **Blocked By**: Tasks 3, 6

    **References**:

    **Pattern References**:
    - `Makefile` (current, 12 lines) - Existing targets to preserve
    - `pyproject.toml` `[dependency-groups] dev` (after Task 3) - Source of truth for `uv sync --group dev`
    - `AGENTS.md:43-44` - Confirms `pre-commit install` workflow

    **External References**:
    - `uv sync --group` docs: `https://docs.astral.sh/uv/concepts/projects/sync/` - Verifies the exact flag
    - `conda env export` docs: `https://docs.conda.io/projects/conda/en/latest/commands/env/export.html` - Confirms behavior with build hashes

    **WHY Each Reference Matters**:
    - The Makefile requires TABs (POSIX make); accidental space-conversion breaks the entire file
    - `uv sync --group dev` semantics differ from `uv pip install --group dev` re: active-env handling; Oracle phase 1 flagged this as needing verification at Task 10 install time

    **Acceptance Criteria**:
    - [ ] `make -n create-dev` exits 0 and printed commands include `conda env update`, `uv sync --group dev` (or `uv pip install --group dev`), `pre-commit install`
    - [ ] `make -n create-dev` does NOT print `pip install -r requirements.txt`
    - [ ] `make -n freeze` exits 0 and printed commands include `conda env export` piped to `grep -v "^prefix:"` redirected to `environment.yaml`
    - [ ] `grep -n "conda-lock" Makefile` returns empty
    - [ ] `grep -nE "paraview_mcp\s" Makefile` returns 0 lines for console-script form (if any existed)
    - [ ] Makefile indentation: `cat -A Makefile | grep "^I" | wc -l` returns > 0 (TABs preserved)

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: Makefile dry-runs succeed
      Tool: Bash
      Preconditions: Tasks 3 (pyproject dev group) and 6 (requirements.txt deleted) complete
      Steps:
        1. Run: make -n create-dev > .omo/evidence/task-7-create-dev-dryrun.txt 2>&1
        2. Assert: exit code 0
        3. Run: make -n freeze > .omo/evidence/task-7-freeze-dryrun.txt 2>&1
        4. Assert: exit code 0
        5. Assert: ! grep -q "pip install -r requirements.txt" .omo/evidence/task-7-create-dev-dryrun.txt
        6. Assert: grep -q "uv sync --group dev\|uv pip install --group dev" .omo/evidence/task-7-create-dev-dryrun.txt
        7. Assert: grep -q "conda env export" .omo/evidence/task-7-freeze-dryrun.txt
        8. Assert: grep -q "grep -v \"\^prefix:\"" .omo/evidence/task-7-freeze-dryrun.txt
      Expected Result: Both targets dry-run successfully with expected commands
      Failure Indicators: non-zero exit, missing or extra commands
      Evidence: .omo/evidence/task-7-create-dev-dryrun.txt, .omo/evidence/task-7-freeze-dryrun.txt

    Scenario: No conda-lock or underscore-script references
      Tool: Bash
      Steps:
        1. Run: { grep -n "conda-lock" Makefile; grep -nE "^\s*paraview_mcp\s" Makefile; } > .omo/evidence/task-7-forbidden-strings.txt 2>&1
        2. Assert: file is empty
      Expected Result: Empty file (no forbidden strings)
      Evidence: .omo/evidence/task-7-forbidden-strings.txt

    Scenario: Indentation preserved (TABs not spaces)
      Tool: Bash
      Steps:
        1. Run: cat -A Makefile | grep -cE "^\^I" > .omo/evidence/task-7-tab-count.txt
        2. Assert: integer value >= 3 (at least 3 TAB-indented recipe lines)
      Expected Result: TAB indentation preserved; Makefile remains parseable by GNU make
      Evidence: .omo/evidence/task-7-tab-count.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-7-create-dev-dryrun.txt`
    - [ ] `.omo/evidence/task-7-freeze-dryrun.txt`
    - [ ] `.omo/evidence/task-7-forbidden-strings.txt`
    - [ ] `.omo/evidence/task-7-tab-count.txt`

    **Commit**: NO (user defers all commits)

- [x]   8. Cross-file consistency sweep (script name, repo URL, stale commands)

    **What to do**:
    - With Tasks 2, 4, 5, 7 complete, run a battery of consistency greps across ALL changed files to catch any missed inconsistencies before the integration install (Task 10)
    - For each grep below, capture results; if any check fails, FIX the offending file and re-run the failing check until it passes
    - Tests:
        1. Console-script name uniformity: `grep -rnE "^\s*paraview_mcp\s+--" README.md AGENTS.md Makefile` -> MUST be empty
        2. Hyphen form present where expected: `grep -rE "paraview-mcp\s+--server" README.md AGENTS.md Makefile` -> at least one match in README, one in AGENTS.md
        3. Repo URL uniformity: `grep -rn "LLNL/paraview_mcp" README.md AGENTS.md` -> MUST be empty
        4. `git clone` URL: `grep -rE "git clone.*paraview_mcp" README.md` -> if any matches, MUST use `NicholasSynovic/paraview_mcp.git`
        5. Stale `python pvserver`: `grep -rn "python pvserver" README.md AGENTS.md` -> MUST be empty
        6. Stale file name: `grep -rn "paraview_mcp_server\.py" README.md AGENTS.md Makefile pyproject.toml` -> MUST be empty
        7. No conda-lock leakage: `grep -rn "conda-lock\|conda_lock" README.md AGENTS.md Makefile pyproject.toml environment.yaml` -> MUST be empty
        8. NOTICE link present in README: `grep -n "NOTICE" README.md` -> MUST return >= 1 match
        9. environment.yaml channels: `grep -A3 "^channels:" environment.yaml | grep -w "defaults"` -> MUST be empty
        10. environment.yaml no prefix: `grep -n "^prefix:" environment.yaml` -> MUST be empty
        11. environment.yaml no self-ref: `grep -n "paraview-mcp==0.1.0\|paraview_mcp==0.1.0" environment.yaml` -> MUST be empty
        12. pyproject script unchanged: `grep -n 'paraview-mcp = "paraview_mcp.main:main"' pyproject.toml` -> MUST return exactly 1 match
    - Save aggregated pass/fail to `.omo/evidence/task-8-consistency-report.txt`

    **Must NOT do**:
    - Do NOT make architectural changes; only fix inconsistencies (string-level edits) within existing tasks' scope
    - Do NOT touch `paraview_mcp/*.py`
    - Do NOT touch `NOTICE`
    - Do NOT touch `.pre-commit-config.yaml`

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Mechanical grep battery with surgical fixes; no design judgment.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Task 9 in Wave 3)
    - **Parallel Group**: Wave 3
    - **Blocks**: F1-F4
    - **Blocked By**: Tasks 2, 4, 5, 7

    **References**:

    **Pattern References**:
    - All in-scope files: `environment.yaml`, `pyproject.toml`, `Makefile`, `README.md`, `AGENTS.md`
    - `pyproject.toml:34-35` - Canonical hyphen form
    - Task 4 acceptance criteria - Already enforces many of these on README; this task is the cross-file sweep

    **WHY Each Reference Matters**:
    - Tasks 2-7 each enforce checks within their own file; this task catches mismatches BETWEEN files (e.g., README uses hyphen, AGENTS.md still has underscore in one spot the Task 5 author missed)

    **Acceptance Criteria**:
    - [ ] All 12 grep checks above pass
    - [ ] `.omo/evidence/task-8-consistency-report.txt` exists, contains all 12 checks with PASS markers
    - [ ] If any check failed-then-fixed, evidence shows the fix file:line

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: Full consistency sweep
      Tool: Bash
      Preconditions: Tasks 2, 4, 5, 7 complete
      Steps:
        1. Run each of the 12 checks above; append PASS/FAIL line to .omo/evidence/task-8-consistency-report.txt
        2. If any FAIL: print offending file:line, fix it, re-run that check
        3. Final assertion: ! grep -q "FAIL" .omo/evidence/task-8-consistency-report.txt
      Expected Result: Report shows 12 PASS lines, zero FAIL
      Failure Indicators: any FAIL line in final report, missing report file
      Evidence: .omo/evidence/task-8-consistency-report.txt

    Scenario: NOTICE reference exists in README
      Tool: Bash
      Steps:
        1. Run: grep -n "NOTICE" README.md > .omo/evidence/task-8-notice-ref.txt
        2. Assert: file non-empty
      Expected Result: README links to NOTICE
      Evidence: .omo/evidence/task-8-notice-ref.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-8-consistency-report.txt`
    - [ ] `.omo/evidence/task-8-notice-ref.txt`

    **Commit**: NO (user defers all commits)

- [x]   9. NOTICE byte-identity verification

    **What to do**:
    - Compute a SHA-256 hash of `NOTICE` BEFORE any task runs (capture from `git show HEAD:NOTICE | sha256sum`)
    - After Wave 2 completes (Tasks 2-6) and after Task 8 consistency sweep, recompute the SHA-256 of the working-tree `NOTICE` file
    - Assert the two hashes match exactly
    - Also assert `git diff NOTICE` returns empty
    - Also assert `git diff --stat NOTICE` returns empty
    - Also assert byte count matches: `wc -c NOTICE` returns identical byte count before and after

    **Must NOT do**:
    - Do NOT modify NOTICE under any circumstance
    - Do NOT create NOTICE.bak or any sibling file
    - Do NOT skip this check even if it "feels" redundant - it is the legal-compliance gate

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Two hash computations + diff check.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Task 8 in Wave 3)
    - **Parallel Group**: Wave 3
    - **Blocks**: F1-F4
    - **Blocked By**: Task 4 (the only task that has any plausible reason to interact with NOTICE, via the README reference)

    **References**:

    **Pattern References**:
    - `NOTICE` (16 lines, LLNL/DOE legal boilerplate) - The file under protection
    - `AGENTS.md` - Confirms NOTICE preservation is non-negotiable
    - `LICENSE` (Apache-2.0) + NOTICE - Together satisfy the Apache-2.0 + BSD-3 attribution requirements inherited from LLNL upstream

    **External References**:
    - Apache-2.0 attribution requirements section 4(d): `https://www.apache.org/licenses/LICENSE-2.0` - Explains why NOTICE must be preserved verbatim when redistributing

    **WHY Each Reference Matters**:
    - The Apache-2.0 link is the authoritative source for WHY this check exists - without it, future maintainers may "clean up" NOTICE and create a license violation

    **Acceptance Criteria**:
    - [ ] `git diff NOTICE` returns empty
    - [ ] `git diff --stat NOTICE` returns empty
    - [ ] SHA-256 of `NOTICE` matches SHA-256 of `git show HEAD:NOTICE`
    - [ ] `wc -c NOTICE` byte count matches `git show HEAD:NOTICE | wc -c`
    - [ ] No file named `NOTICE.bak`, `NOTICE.orig`, `NOTICE.tmp`, or similar exists at repo root

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: NOTICE byte-identical to HEAD
      Tool: Bash
      Preconditions: Plan execution underway; NOTICE was untouched at start
      Steps:
        1. Run: git show HEAD:NOTICE | sha256sum > .omo/evidence/task-9-notice-head-sha.txt
        2. Run: sha256sum NOTICE > .omo/evidence/task-9-notice-working-sha.txt
        3. Assert: cut -d' ' -f1 .omo/evidence/task-9-notice-head-sha.txt == cut -d' ' -f1 .omo/evidence/task-9-notice-working-sha.txt
        4. Run: git diff NOTICE > .omo/evidence/task-9-notice-diff.txt
        5. Assert: .omo/evidence/task-9-notice-diff.txt is empty (0 bytes)
      Expected Result: SHA-256 hashes match; git diff empty
      Failure Indicators: SHA mismatch, non-empty diff, NOTICE.bak or similar present
      Evidence: .omo/evidence/task-9-notice-head-sha.txt, .omo/evidence/task-9-notice-working-sha.txt, .omo/evidence/task-9-notice-diff.txt

    Scenario: No sibling/backup files leaked into repo root
      Tool: Bash
      Steps:
        1. Run: ls NOTICE.bak NOTICE.orig NOTICE.tmp NOTICE.old 2>/dev/null > .omo/evidence/task-9-no-siblings.txt
        2. Assert: .omo/evidence/task-9-no-siblings.txt is empty
      Expected Result: Empty file (no backup siblings)
      Evidence: .omo/evidence/task-9-no-siblings.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-9-notice-head-sha.txt`
    - [ ] `.omo/evidence/task-9-notice-working-sha.txt`
    - [ ] `.omo/evidence/task-9-notice-diff.txt`
    - [ ] `.omo/evidence/task-9-no-siblings.txt`

    **Commit**: NO (user defers all commits)

- [x]   10. Full conda env install + smoke test (the long integration QA)

    **What to do**:
    - This is the heavyweight verification: prove the cleaned `environment.yaml` + new `pyproject.toml` dev group actually builds a working env from scratch on linux-64
    - Use a UNIQUE env name to avoid clobbering the user's existing env: `paraview_mcp_qa_$(date +%s)` or similar; record the chosen name in evidence
    - Steps (run from repo root):
        1. `conda env create -f environment.yaml -n <qa-name>` (5-15 minutes; capture full stdout+stderr)
        2. `conda run -n <qa-name> pip install -e .` (installs the local package into the new env)
        3. `conda run -n <qa-name> which paraview-mcp` (confirms console script registered)
        4. `conda run -n <qa-name> python -c "import paraview.simple; print('paraview.simple OK')"` (confirms paraview package is importable)
        5. `conda run -n <qa-name> python -c "import paraview_mcp.main; print('paraview_mcp OK')"` (confirms our package imports - this WILL fail at runtime if paraview.simple is broken, so this is a downstream smoke test)
        6. `conda run -n <qa-name> uv sync --group dev` (installs dev tools per pyproject); if this command tries to create a project-local `.venv` instead of using the conda env, fall back to `conda run -n <qa-name> uv pip install --group dev` per Oracle phase 1 note - capture which form was used to evidence
        7. `conda run -n <qa-name> which pre-commit` (confirms dev tool installed)
        8. `conda run -n <qa-name> which uv` (confirms uv installed)
    - Teardown (MANDATORY even on failure): `conda env remove -n <qa-name> -y`
    - If ANY step fails, capture the failure, run teardown, and report which step failed with the offending stdout/stderr
    - This task is the gate that proves the full reproducibility story works

    **Must NOT do**:
    - Do NOT clobber the user's existing `paraview_mcp` conda env - always use a unique QA env name
    - Do NOT skip teardown even on failure (leftover envs waste 10+ GB)
    - Do NOT run `pvserver` as part of this task (that requires a separate process + user interaction; out of scope for headless QA)
    - Do NOT modify any source file in response to install failures - report and halt for user

    **Recommended Agent Profile**:
    - **Category**: `unspecified-high`
        - Reason: Long-running multi-step install that requires careful error handling, fallback logic for `uv sync` behavior, and guaranteed teardown.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: NO (it is the sole Wave 4 task; runs after all other implementation work)
    - **Parallel Group**: Wave 4 (alone)
    - **Blocks**: F1-F4
    - **Blocked By**: Tasks 2, 3, 6, 7

    **References**:

    **Pattern References**:
    - `environment.yaml` (after Task 2) - The file under test
    - `pyproject.toml` (after Task 3) - Source of `[dependency-groups] dev`
    - `Makefile` (after Task 7) - `create-dev` target uses the same `uv sync --group dev` pattern; this task validates that path
    - `AGENTS.md:50-56` - Confirms `pip install -e .` is required for console script to register

    **External References**:
    - `conda env create` docs: `https://docs.conda.io/projects/conda/en/latest/commands/env/create.html`
    - `conda run` docs: `https://docs.conda.io/projects/conda/en/latest/commands/run.html` - For running commands in a non-activated env
    - `uv sync --group` behavior: `https://docs.astral.sh/uv/concepts/projects/sync/` - Reference for fallback decision

    **WHY Each Reference Matters**:
    - `AGENTS.md:50-56` is the source-of-truth note that `pip install -e .` is REQUIRED (without it, the import fails with "no module named paraview_mcp"); skipping this step gives a false negative
    - `conda run` avoids the need to source activate scripts in non-interactive contexts; using `conda activate` in a script often fails silently in CI/agent environments

    **Acceptance Criteria**:
    - [ ] `conda env create -f environment.yaml -n <qa-name>` exits 0
    - [ ] `conda run -n <qa-name> which paraview-mcp` prints a path inside the env (`.../envs/<qa-name>/bin/paraview-mcp`)
    - [ ] `conda run -n <qa-name> python -c "import paraview.simple"` exits 0
    - [ ] `conda run -n <qa-name> python -c "import paraview_mcp.main"` exits 0
    - [ ] `conda run -n <qa-name> uv sync --group dev` OR `conda run -n <qa-name> uv pip install --group dev` exits 0 (record which form was used)
    - [ ] `conda run -n <qa-name> which pre-commit` prints a path
    - [ ] `conda run -n <qa-name> which uv` prints a path
    - [ ] `conda env remove -n <qa-name> -y` exits 0 (teardown succeeded)
    - [ ] No env named `<qa-name>` remains after teardown: `conda env list | grep -c "<qa-name>"` returns 0

    **QA Scenarios (MANDATORY)**:

    ```
    Scenario: Happy path - clean env builds end-to-end
      Tool: Bash
      Preconditions: Tasks 2, 3, 6, 7 complete; conda CLI on PATH; ~15 GB free disk
      Steps:
        1. Run: QA_ENV="paraview_mcp_qa_$(date +%s)" && echo "$QA_ENV" > .omo/evidence/task-10-env-name.txt
        2. Run: conda env create -f environment.yaml -n "$QA_ENV" > .omo/evidence/task-10-env-create.log 2>&1
        3. Assert: exit code 0
        4. Run: conda run -n "$QA_ENV" pip install -e . > .omo/evidence/task-10-pip-install-e.log 2>&1
        5. Assert: exit code 0
        6. Run: conda run -n "$QA_ENV" which paraview-mcp > .omo/evidence/task-10-which-paraview-mcp.txt
        7. Assert: file contains "envs/$QA_ENV/bin/paraview-mcp"
        8. Run: conda run -n "$QA_ENV" python -c "import paraview.simple; print('OK')" > .omo/evidence/task-10-import-paraview.txt 2>&1
        9. Assert: file contains "OK" and no traceback
        10. Run: conda run -n "$QA_ENV" python -c "import paraview_mcp.main; print('OK')" > .omo/evidence/task-10-import-paraview-mcp.txt 2>&1
        11. Assert: file contains "OK"
        12. Try: conda run -n "$QA_ENV" uv sync --group dev > .omo/evidence/task-10-uv-sync.log 2>&1; if exit != 0, run conda run -n "$QA_ENV" uv pip install --group dev > .omo/evidence/task-10-uv-pip-install.log 2>&1
        13. Assert: at least one of the two log files shows exit 0; record which form worked in .omo/evidence/task-10-uv-form.txt
        14. Run: conda run -n "$QA_ENV" which pre-commit > .omo/evidence/task-10-which-precommit.txt
        15. Run: conda run -n "$QA_ENV" which uv > .omo/evidence/task-10-which-uv.txt
        16. Assert: both `which` outputs contain "envs/$QA_ENV/bin/"
      Expected Result: All assertions pass; QA env exists with all expected binaries
      Failure Indicators: conda env create resolver conflict, ImportError on paraview.simple, missing console script, uv install fails with both forms
      Evidence: all .omo/evidence/task-10-*.log and .txt files listed above

    Scenario: Teardown (MANDATORY - runs even on happy-path failure)
      Tool: Bash
      Preconditions: QA env exists (or partially exists from failed create)
      Steps:
        1. Read env name from .omo/evidence/task-10-env-name.txt
        2. Run: conda env remove -n "$QA_ENV" -y > .omo/evidence/task-10-teardown.log 2>&1
        3. Run: conda env list | grep -c "$QA_ENV" > .omo/evidence/task-10-env-list-after.txt
        4. Assert: integer value == 0
      Expected Result: QA env removed; system disk reclaimed
      Failure Indicators: env still listed (manual cleanup needed)
      Evidence: .omo/evidence/task-10-teardown.log, .omo/evidence/task-10-env-list-after.txt

    Scenario: Failure mode - paraview-mcp script missing
      Tool: Bash
      Preconditions: `pip install -e .` step failed or did not register the console script
      Steps:
        1. If `which paraview-mcp` returns non-zero or path outside env:
           a. Capture `conda run -n "$QA_ENV" pip show paraview-mcp` to evidence
           b. Capture `conda run -n "$QA_ENV" pip list | grep paraview` to evidence
           c. Report failure + halt; do NOT proceed to F1-F4
        2. Run teardown scenario regardless
      Expected Result: Failure is detected, fully captured, teardown still runs, F1-F4 do not start
      Evidence: .omo/evidence/task-10-failure-*.txt
    ```

    **Evidence to Capture**:
    - [ ] `.omo/evidence/task-10-env-name.txt`
    - [ ] `.omo/evidence/task-10-env-create.log`
    - [ ] `.omo/evidence/task-10-pip-install-e.log`
    - [ ] `.omo/evidence/task-10-which-paraview-mcp.txt`
    - [ ] `.omo/evidence/task-10-import-paraview.txt`
    - [ ] `.omo/evidence/task-10-import-paraview-mcp.txt`
    - [ ] `.omo/evidence/task-10-uv-sync.log` and/or `.omo/evidence/task-10-uv-pip-install.log`
    - [ ] `.omo/evidence/task-10-uv-form.txt`
    - [ ] `.omo/evidence/task-10-which-precommit.txt`
    - [ ] `.omo/evidence/task-10-which-uv.txt`
    - [ ] `.omo/evidence/task-10-teardown.log`
    - [ ] `.omo/evidence/task-10-env-list-after.txt`

    **Commit**: NO (user defers all commits)

---

## Final Verification Wave (MANDATORY - after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.

- [x] F1. **Plan Compliance Audit** - `oracle`

    Read this plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns - reject with file:line if found. Specifically:
    - `grep -rn "conda-lock" .` MUST return only this plan/draft (no source files)
    - `grep -rn "defaults" environment.yaml` MUST return empty
    - `grep -rn "prefix:" environment.yaml` MUST return empty
    - `grep -rn "paraview-mcp==0.1.0" environment.yaml` MUST return empty
    - `git diff --stat NOTICE` MUST return empty (file unchanged)
    - `ls requirements.txt` MUST fail (file deleted)
    - `grep -rn "python pvserver" README.md` MUST return empty
    - `grep -rn "LLNL/paraview_mcp" README.md` MUST return empty
    - `grep -rn "paraview_mcp" README.md AGENTS.md Makefile | grep -v "paraview_mcp\.main\|paraview_mcp/\|paraview_mcp\s*$"` MUST show no console-script form
      Check evidence files exist in `.omo/evidence/`. Compare deliverables against plan.

    Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code/Config Quality Review** - `unspecified-high`

    Run lint-equivalents: `python -c "import yaml; yaml.safe_load(open('environment.yaml'))"`, `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`, `make -n create-dev`, `make -n freeze`. Review all changed files for: trailing whitespace, mixed indentation, inconsistent quoting style, dead/commented-out config blocks, generic placeholder text ("TODO", "FIXME", "XXX"). Check for AI slop: filler bullet points, marketing fluff in README ("blazing fast", "revolutionary"), tautological sentences, excessive emoji.

    Output: `YAML [PASS/FAIL] | TOML [PASS/FAIL] | Makefile [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA on README** - `unspecified-high`

    Start from clean state. Render README in a markdown viewer (look_at tool). Walk through it as a new user would:
    - Click every ToC link; confirm it lands on the right section
    - Read the install steps top-to-bottom; check that they're internally consistent (no forward references to undefined env vars, no missing steps)
    - Confirm the mermaid diagram has correct syntax (paste into mermaid.live or use look_at)
    - Run every shell command in the install + run sections in a scratch dir (separate from the Task 10 install env) to detect ordering bugs
    - Test every URL: `curl -I -L $URL` returns 2xx for each
    - Verify OpenCode config JSON snippet is valid JSON: `python -c "import json; json.loads(open('snippet.json').read())"`
    - Verify Claude Code config JSON snippet is valid JSON
    - Save evidence to `.omo/evidence/final-qa/`

    Output: `ToC [N/N] | Commands [N/N pass] | URLs [N/N 2xx] | JSON [N/N valid] | VERDICT`

- [x] F4. **Scope Fidelity Check** - `deep`

    For each task 1-10: read "What to do", read actual `git diff` of changed files. Verify 1:1 - everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance per-task. Detect cross-task contamination: e.g., Task 4 (README) touching `pyproject.toml`, or Task 7 (Makefile) touching `paraview_mcp/*.py`. Flag any unaccounted changes (files modified that no task claims responsibility for).

    Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

> User does NOT commit during agent sessions (GPG blocker). All commits are deferred to the user post-completion. The plan produces clean changes ready for review but does NOT run `git commit` at any point.

- **Suggested commit grouping (for user reference only - executor will NOT run these)**:
    - `chore(env): clean environment.yaml, drop conda-lock plans, switch to conda-forge+nodefaults` - environment.yaml only
    - `chore(deps): consolidate dev tooling into pyproject.toml dependency-groups, delete requirements.txt` - pyproject.toml + delete requirements.txt
    - `chore(make): add freeze target, drop requirements.txt path, hyphenate script name` - Makefile only
    - `docs(readme): full rewrite with ToC, MCP intro, integrations, troubleshooting, maintenance` - README.md only
    - `docs(agents): standardize on paraview-mcp (hyphen) console-script form` - AGENTS.md only

---

## Success Criteria

### Verification Commands

```bash
# Static
python -c "import yaml; yaml.safe_load(open('environment.yaml'))"   # exit 0
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"  # exit 0
make -n create-dev                                                   # exit 0
make -n freeze                                                       # exit 0
test ! -f requirements.txt                                           # exit 0
git diff --stat NOTICE                                               # empty output

# Stale-string greps
! grep -n "python pvserver" README.md
! grep -n "LLNL/paraview_mcp" README.md
! grep -n "conda-lock" README.md AGENTS.md Makefile pyproject.toml environment.yaml
! grep -n "^prefix:" environment.yaml
! grep -n "^channels:" -A3 environment.yaml | grep -w "defaults"

# Install (slow, ~5-15 min)
conda env create -f environment.yaml -n paraview_mcp_qa
conda run -n paraview_mcp_qa pip install -e .
conda run -n paraview_mcp_qa which paraview-mcp        # returns path
conda run -n paraview_mcp_qa python -c "import paraview.simple"  # exit 0
conda env remove -n paraview_mcp_qa -y
```

### Final Checklist

- [ ] All "Must Have" items verified present
- [ ] All "Must NOT Have" items verified absent
- [ ] All 10 implementation tasks completed
- [ ] All F1-F4 reviewers returned APPROVE
- [ ] User has given explicit "okay" after reviewing F1-F4 results
- [ ] Draft `.omo/drafts/reproducibility-and-readme.md` deleted
