# Makefile create-dev Target Update

## TL;DR

> **Quick Summary**: Replace the broken `create-dev` Makefile recipe with a conda-env-aware, idempotent setup using `conda env update --prune` + `conda run -n paraview_mcp` wrapping for pre-commit and uv. Add `.PHONY` declaration. Remove `conda init` and `pre-commit autoupdate`.
>
> **Deliverables**:
> - Updated `Makefile` with new `create-dev` body and `.PHONY` declaration
> - `build` target body unchanged
> - No git commit (user handles)
>
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - sequential (single file, single concern)
> **Critical Path**: Task 1 → Task 2 → F1-F4 → user okay

---

## Context

### Original Request
> "Update `create-dev` to: create conda env from environment.yaml, activate it, configure pre-commit, then sync uv. Do NOT commit (user handles)."

### Interview Summary
**Key Discussions**:
- Make recipe activation problem: each line runs in a fresh subshell, so `conda activate` doesn't persist → Decision: use `conda run -n <env> <cmd>` per line
- Current `conda create --file environment.yaml` is wrong syntax for env YAMLs → Decision: switch to `conda env update --file environment.yaml --prune` (also handles existing env)
- `conda init` is a one-time user-shell config, not project setup → Decision: remove
- Keep `rm -rf .venv && uv sync` pattern → Decision: keep, but wrap `uv sync` with `conda run`
- Pre-commit + uv pinned in `environment.yaml` pip section → Decision: wrap them with `conda run -n paraview_mcp` so the env's pinned versions are used

**Research Findings**:
- `environment.yaml` line 1: `name: paraview_mcp` (env name confirmed)
- `environment.yaml` lines 168-180: pip section includes `pre-commit==4.6.0`, `uv==0.11.18`, `virtualenv==21.4.2`
- `Makefile` build target (lines 1-5) uses bare `uv` — same inconsistency exists but is OUT OF SCOPE
- Current `create-dev` recipe (lines 7-13) is broken and ungrouped

### Metis Review
**Identified Gaps** (addressed):
- `--prune` destructiveness → User chose KEEP (strict idempotency)
- `pre-commit autoupdate` modifies tracked `.pre-commit-config.yaml` on every run → User chose REMOVE
- `.PHONY` not declared → User chose ADD for both `build` and `create-dev`
- Tab vs space sensitivity → Locked as guardrail
- Scope creep into `build` target → Locked as guardrail
- `prefix:` hardcoded in environment.yaml → Out of scope (separate issue)

---

## Work Objectives

### Core Objective
Replace the broken `create-dev` target body and add a `.PHONY` declaration so `make create-dev` reliably and idempotently builds the project's dev environment.

### Concrete Deliverables
- `Makefile` line 1 (new): `.PHONY: build create-dev`
- `Makefile` line 2 (new): blank line
- `Makefile` `create-dev` recipe body replaced (4 commands)
- `Makefile` `build` target body unchanged (byte-identical)

### Definition of Done
- [ ] `make --dry-run create-dev` prints the new recipe with no parse error
- [ ] `grep` checks (see Verification Strategy) all pass
- [ ] `build` recipe body byte-identical to pre-change state
- [ ] No commit made

### Must Have
- `.PHONY: build create-dev` as the first non-blank line of `Makefile`
- `create-dev` recipe body exactly:
  ```
  	conda env update --file environment.yaml --prune
  	conda run -n paraview_mcp pre-commit install
  	rm -rf .venv
  	conda run -n paraview_mcp uv sync
  ```
- All recipe lines indented with tab characters (not spaces)
- `build` target preserved with its existing 4-line body
- No `conda init`, no `pre-commit autoupdate`, no `conda create --file` anywhere in `Makefile`

### Must NOT Have (Guardrails)
- NO modifications to the `build` target body (lines currently 2-5)
- NO modifications to `environment.yaml`
- NO modifications to `.pre-commit-config.yaml`
- NO modifications to `pyproject.toml`
- NO git commit, git add, or git stash actions
- NO echo/logging additions to the recipe
- NO PATH guards (`which conda || exit`) or conda-bootstrap logic
- NO `.ONESHELL:` directive
- NO `SHELL :=` override
- NO chaining commands with `&&` on a single line (each command on its own line)
- NO conversion of recipe indentation from tabs to spaces
- NO documentation updates to README.md or AGENTS.md
- NO new Makefile targets beyond what exists
- NO touching the staged-but-uncommitted files from the prior boulder (pyproject.toml, paraview_mcp/main.py, README.md, AGENTS.md)

### Spec Framework Integration
- **Detected Framework**: None
- (No SDD framework directories present — `openspec/`, `.specify/` absent)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: NO (repo has no test suite; this is a Makefile edit)
- **Automated tests**: None — Makefile syntax + content verification is the appropriate test surface
- **Framework**: N/A
- **Verification approach**: agent-executed `grep`, `make --dry-run`, `cat -A`, `git diff` assertions

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Makefile syntax**: Use Bash (`make --dry-run`) — validates parse + recipe expansion
- **Content correctness**: Use Bash (`grep -c`) — validates exact lines present/absent
- **Indent correctness**: Use Bash (`cat -A`) — validates tabs not spaces
- **Build preservation**: Use Bash (`git diff` + `sed`) — validates byte-identical build body
- **End-to-end**: Use Bash (run `make --dry-run create-dev` and verify output)

> **Note**: Actually running `make create-dev` (i.e., letting it create the conda env) is OUT of QA scope — it requires network, takes minutes, and mutates the developer's machine. Verification is limited to Makefile correctness, not env-build execution. The user runs `make create-dev` themselves to validate end-to-end behavior.

---

## Execution Strategy

### Parallel Execution Waves

> Tiny single-file change. No meaningful parallelism. Two sequential tasks then 4-way final review.

```
Wave 1 (Start Immediately):
└── Task 1: Update Makefile (add .PHONY + replace create-dev body) [quick]

Wave 2 (After Wave 1):
└── Task 2: Verify Makefile correctness with grep + make --dry-run [quick]

Wave FINAL (After Wave 2 — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code/Makefile quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 2 → F1-F4 → user okay
Parallel Speedup: N/A (single-file edit)
Max Concurrent: 4 (final wave only)
```

### Dependency Matrix
- **Task 1**: blocked by none → blocks Task 2 → enables final wave
- **Task 2**: blocked by Task 1 → blocks final wave
- **F1-F4**: blocked by Tasks 1-2 → all run in parallel → blocks user okay

### Agent Dispatch Summary
- **Wave 1**: 1 task — Task 1 → `quick`
- **Wave 2**: 1 task — Task 2 → `quick`
- **Wave FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Update Makefile (add .PHONY + replace create-dev body)

  **What to do**:
  - Open `/home/nicholas/Documents/projects/paraview_mcp/Makefile`
  - At the top of the file (before the existing `build:` line), insert `.PHONY: build create-dev` followed by one blank line
  - Replace the entire `create-dev` recipe (currently lines 7-13: target line + 6 command lines including `conda init`, `conda create --file environment.yaml`, `pre-commit install`, `pre-commit autoupdate`, `rm -rf .venv`, `uv sync`) with this exact body:
    ```
    create-dev:
    	conda env update --file environment.yaml --prune
    	conda run -n paraview_mcp pre-commit install
    	rm -rf .venv
    	conda run -n paraview_mcp uv sync
    ```
  - All 4 command lines under `create-dev:` MUST start with a literal TAB character (ASCII 0x09), NOT spaces
  - Preserve the `build` target body byte-for-byte (do NOT touch lines 2-5)
  - Preserve the existing blank line between `build` and `create-dev` targets
  - Save file; do NOT git add, do NOT commit

  **Must NOT do**:
  - Do NOT modify the `build` target body
  - Do NOT add `.ONESHELL:` or `SHELL :=` directives
  - Do NOT add echo/logging commands
  - Do NOT add PATH guards or `which conda` checks
  - Do NOT chain commands with `&&`
  - Do NOT replace tabs with spaces (Makefile syntax requires tabs)
  - Do NOT git add or commit
  - Do NOT touch any other file

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-file Makefile edit with ≤15 lines of change, no logic, no abstractions
  - **Skills**: (none)
    - No domain-specific skill applies for a Makefile patch
  - **Skills Evaluated but Omitted**:
    - `git-master`: omitted — user will commit themselves, no git ops needed
    - any test skill: omitted — no test suite to author

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 1, alone)
  - **Blocks**: Task 2, F1-F4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `/home/nicholas/Documents/projects/paraview_mcp/Makefile:1-5` — Existing `build` target showing tab-indented recipe style; preserve byte-for-byte
  - `/home/nicholas/Documents/projects/paraview_mcp/Makefile:7-13` — Existing `create-dev` recipe to be replaced

  **API/Type References** (contracts to implement against):
  - `/home/nicholas/Documents/projects/paraview_mcp/environment.yaml:1` — `name: paraview_mcp` (the env name `conda run -n` must reference)
  - `/home/nicholas/Documents/projects/paraview_mcp/environment.yaml:168-180` — pip section providing `pre-commit==4.6.0`, `uv==0.11.18` inside the env

  **External References**:
  - `man conda-env` — `conda env update --file <yaml> --prune` semantics: creates env if missing, updates if present; `--prune` removes packages not declared in YAML
  - `conda run --help` — `conda run -n <env> <cmd>` semantics: executes `<cmd>` with the env's PATH/Python prefixed, without persisting activation
  - GNU Make manual, section "Recipe Syntax" — recipe lines MUST start with a tab character

  **WHY Each Reference Matters**:
  - `Makefile:1-5` — Must remain byte-identical; verification step relies on this invariant
  - `Makefile:7-13` — This is the exact region being replaced; do not partially overlap or leave fragments
  - `environment.yaml:1` — `paraview_mcp` is the literal env name in `conda run -n paraview_mcp`; misspelling breaks every subsequent line
  - `environment.yaml:168-180` — Confirms `pre-commit` and `uv` are inside the conda env, validating the `conda run` wrapping strategy
  - `conda env update` man — Behavior is "create if missing OR update if present", which is why this single command replaces the broken `conda create --file` AND removes the need for env-existence branching
  - GNU Make recipe syntax — A space-indented recipe line produces `Makefile:N: *** missing separator. Stop.`; this is the #1 failure mode for Makefile edits

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: Makefile is syntactically valid after edit
    Tool: Bash
    Preconditions: Task 1 edits applied
    Steps:
      1. Run: cd /home/nicholas/Documents/projects/paraview_mcp && make --dry-run create-dev > .omo/evidence/task-1-make-dry-run.txt 2>&1
      2. Check exit code is 0
      3. Assert output contains "conda env update --file environment.yaml --prune"
      4. Assert output contains "conda run -n paraview_mcp pre-commit install"
      5. Assert output contains "rm -rf .venv"
      6. Assert output contains "conda run -n paraview_mcp uv sync"
      7. Assert output does NOT contain "missing separator"
    Expected Result: Exit code 0, all 4 expected commands present, no parser errors
    Failure Indicators: Non-zero exit, "missing separator" message, missing/extra commands
    Evidence: .omo/evidence/task-1-make-dry-run.txt

  Scenario: Indentation uses tabs, not spaces
    Tool: Bash
    Preconditions: Task 1 edits applied
    Steps:
      1. Run: cat -A /home/nicholas/Documents/projects/paraview_mcp/Makefile > .omo/evidence/task-1-tabs.txt
      2. Assert every recipe command line in output starts with "^I" (tab marker), not spaces
      3. Run: awk '/^[a-zA-Z_-]+:/{intgt=1; next} intgt && NF && !/^\t/{print "SPACE_INDENT_LINE:" NR ":" $0; exit 1} /^$/{intgt=0}' /home/nicholas/Documents/projects/paraview_mcp/Makefile
      4. Assert awk exit code is 0 (no space-indented recipe lines found)
    Expected Result: All recipe lines start with tab; awk exits 0
    Failure Indicators: Any line under `build:` or `create-dev:` starts with spaces; awk exits 1
    Evidence: .omo/evidence/task-1-tabs.txt
  ```

  **Evidence to Capture:**
  - [ ] `.omo/evidence/task-1-make-dry-run.txt` — `make --dry-run create-dev` output
  - [ ] `.omo/evidence/task-1-tabs.txt` — `cat -A Makefile` output

  **Commit**: NO (user handles all commits manually)

- [x] 2. Verify Makefile correctness with grep + diff checks

  **What to do**:
  - Run all acceptance-criteria grep checks from the draft against the edited `Makefile`
  - Capture results to evidence files
  - Run `git diff --no-color Makefile` and verify NO lines from the `build` recipe (lines currently 1-5 of original file) appear in the diff
  - Confirm the only diff hunks are: (a) insertion of `.PHONY: build create-dev` + blank line at top, and (b) replacement of the `create-dev` recipe body

  **Must NOT do**:
  - Do NOT modify any file
  - Do NOT run `make create-dev` for real (would create conda env, slow/mutating)
  - Do NOT git add or commit
  - Do NOT modify the staged files from the prior boulder

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Pure shell-based verification, no logic, ≤10 commands
  - **Skills**: (none)
  - **Skills Evaluated but Omitted**:
    - `git-master`: omitted — only read-only `git diff` usage; no git skill needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 2, alone)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - Draft `.omo/drafts/makefile-create-dev-update.md` "Final Acceptance Criteria" section — exact grep commands and expected counts

  **API/Type References**:
  - `/home/nicholas/Documents/projects/paraview_mcp/Makefile` — file being verified

  **External References**:
  - `grep -c <pattern> <file>` — returns count of matching lines; exit 0 if ≥1 match, 1 if zero
  - `git diff --no-color <file>` — shows unstaged changes relative to HEAD

  **WHY Each Reference Matters**:
  - The draft acceptance-criteria list IS the verification contract; do not invent new checks, run exactly those
  - `grep -c` returning a precise integer is the cleanest agent-executable assertion
  - `git diff` confirms by negative evidence that the `build` recipe was untouched

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: All content-correctness grep checks pass
    Tool: Bash
    Preconditions: Task 1 complete; Makefile in edited state
    Steps:
      1. cd /home/nicholas/Documents/projects/paraview_mcp
      2. Run and capture each:
         - grep -c "^\.PHONY: build create-dev$" Makefile        → expect 1
         - grep -c "conda env update --file environment.yaml --prune" Makefile → expect 1
         - grep -c "conda run -n paraview_mcp pre-commit install" Makefile → expect 1
         - grep -c "conda run -n paraview_mcp uv sync" Makefile  → expect 1
         - grep -c "pre-commit autoupdate" Makefile               → expect 0
         - grep -c "conda init" Makefile                          → expect 0
         - grep -c "conda create --file" Makefile                 → expect 0
      3. Save all 7 outputs to .omo/evidence/task-2-grep-checks.txt with labels
      4. Assert every count matches expected value
    Expected Result: All 7 grep counts match expected values exactly
    Failure Indicators: Any count off by ≥1; missing PHONY; lingering autoupdate/init/create-file
    Evidence: .omo/evidence/task-2-grep-checks.txt

  Scenario: build target body preserved byte-identical
    Tool: Bash
    Preconditions: Task 1 complete
    Steps:
      1. cd /home/nicholas/Documents/projects/paraview_mcp
      2. Extract the build recipe body (4 lines after "build:") from HEAD: git show HEAD:Makefile | awk '/^build:/{flag=1; next} /^[a-zA-Z_-]+:/{flag=0} flag && /^\t/{print}' > .omo/evidence/task-2-build-before.txt
      3. Extract the build recipe body from current working file: awk '/^build:/{flag=1; next} /^[a-zA-Z_-]+:/{flag=0} flag && /^\t/{print}' Makefile > .omo/evidence/task-2-build-after.txt
      4. Run: diff .omo/evidence/task-2-build-before.txt .omo/evidence/task-2-build-after.txt
      5. Assert diff exit code is 0 (files identical)
    Expected Result: build recipe body identical pre/post edit
    Failure Indicators: diff outputs any line difference; non-zero exit code
    Evidence: .omo/evidence/task-2-build-before.txt, .omo/evidence/task-2-build-after.txt

  Scenario: git diff shows only expected hunks
    Tool: Bash
    Preconditions: Task 1 complete
    Steps:
      1. cd /home/nicholas/Documents/projects/paraview_mcp
      2. Run: git diff --no-color Makefile > .omo/evidence/task-2-git-diff.txt
      3. Assert diff contains addition of ".PHONY: build create-dev"
      4. Assert diff contains addition of "conda env update --file environment.yaml --prune"
      5. Assert diff contains addition of "conda run -n paraview_mcp pre-commit install"
      6. Assert diff contains addition of "conda run -n paraview_mcp uv sync"
      7. Assert diff contains removal of "conda init"
      8. Assert diff contains removal of "conda create --file environment.yaml"
      9. Assert diff contains removal of "pre-commit autoupdate"
      10. Assert diff does NOT contain removal of "uv build" or "uv pip install dist" (build recipe untouched)
    Expected Result: Diff hunks match expected additions/removals; no build-recipe touches
    Failure Indicators: Unexpected removal lines from build recipe; missing expected additions
    Evidence: .omo/evidence/task-2-git-diff.txt
  ```

  **Evidence to Capture:**
  - [ ] `.omo/evidence/task-2-grep-checks.txt` — all 7 grep results
  - [ ] `.omo/evidence/task-2-build-before.txt` — pre-edit build body
  - [ ] `.omo/evidence/task-2-build-after.txt` — post-edit build body
  - [ ] `.omo/evidence/task-2-git-diff.txt` — full git diff output

  **Commit**: NO

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.**

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read this plan end-to-end. For each "Must Have": verify the corresponding line/content exists in `Makefile` (grep, line-by-line). For each "Must NOT Have": search `Makefile`, `environment.yaml`, `.pre-commit-config.yaml`, `pyproject.toml`, `README.md`, `AGENTS.md` for forbidden modifications — reject with file:line if found. Confirm `git status` shows ONLY `Makefile` as modified (staged files from prior boulder unchanged). Check all evidence files exist in `.omo/evidence/`.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Makefile Quality Review** — `unspecified-high`
  Review the edited `Makefile` for: tab consistency (no mixed tabs/spaces in any recipe), proper blank-line separation between targets, no trailing whitespace, no accidental BOM, no introduced shell anti-patterns (unquoted variables, missing error handling beyond what's expected for a setup target). Verify `make --dry-run build` and `make --dry-run create-dev` both succeed. Confirm no AI-slop: no excessive comments, no over-engineered conditionals, no premature abstraction.
  Output: `Build dry-run [PASS/FAIL] | Create-dev dry-run [PASS/FAIL] | Indent [CLEAN/ISSUES] | Slop [CLEAN/ISSUES] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from current repo state. Execute EVERY QA scenario from Tasks 1 and 2 — follow exact steps, capture evidence to `.omo/evidence/final-qa/`. Additionally: (a) verify `make` (no target) shows expected default behavior or error consistent with current makefile structure, (b) verify `make --dry-run` for both targets parses cleanly, (c) verify no evidence files from prior boulders were overwritten. Do NOT actually run `make create-dev` (would build conda env).
  Output: `Scenarios [N/N pass] | Edge Cases [N tested] | Evidence [N captured] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Read this plan's "What to do" and "Must NOT do" for each task. Read actual `git diff` for the entire repo. Verify 1:1 — every change in the diff is accounted for by Task 1 or Task 2; nothing outside `Makefile` was modified. Confirm the staged files from the prior boulder (`pyproject.toml`, `paraview_mcp/main.py`, `README.md`, `AGENTS.md`) are unchanged from their pre-task staged state (`git diff --cached` matches their pre-task `git diff --cached`). Detect any cross-task contamination or unaccounted changes anywhere in the working tree.
  Output: `Tasks [2/2 compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | Staged-from-prior-boulder [UNCHANGED/MODIFIED] | VERDICT`

---

## Commit Strategy

**NO COMMITS by the executor. The user will commit manually.**

After F1-F4 approve and the user gives explicit okay, the executor must:
- Leave `Makefile` modified in the working tree
- NOT run `git add Makefile`
- NOT run `git commit`
- Inform the user that the change is ready for their manual commit

Suggested commit message for the user (not executed by agent):
```
chore(makefile): rewrite create-dev for conda env + uv

- Add .PHONY for build and create-dev
- Replace broken `conda create --file` with `conda env update --prune`
- Remove `conda init` (one-time user shell config, not project setup)
- Remove `pre-commit autoupdate` (dirty-tree side effect)
- Wrap pre-commit and uv with `conda run -n paraview_mcp`
```

---

## Success Criteria

### Verification Commands
```bash
cd /home/nicholas/Documents/projects/paraview_mcp

# Parses cleanly
make --dry-run create-dev          # Expected: exit 0, prints 4 commands
make --dry-run build               # Expected: exit 0, prints 4 build commands

# Content checks
grep -c "^\.PHONY: build create-dev$" Makefile                           # Expected: 1
grep -c "conda env update --file environment.yaml --prune" Makefile      # Expected: 1
grep -c "conda run -n paraview_mcp pre-commit install" Makefile          # Expected: 1
grep -c "conda run -n paraview_mcp uv sync" Makefile                     # Expected: 1
grep -c "pre-commit autoupdate" Makefile                                 # Expected: 0
grep -c "conda init" Makefile                                            # Expected: 0
grep -c "conda create --file" Makefile                                   # Expected: 0

# Scope checks
git status --porcelain | grep -v "^M  pyproject.toml\|^M  paraview_mcp/main.py\|^M  README.md\|^M  AGENTS.md" | grep -E "^.M|^M " | grep -v "Makefile"
# Expected: empty (only Makefile newly modified; prior-boulder staged files untouched)
```

### Final Checklist
- [ ] `.PHONY: build create-dev` present at top of Makefile
- [ ] New `create-dev` recipe contains the 4 required commands (in order)
- [ ] No `conda init`, no `pre-commit autoupdate`, no `conda create --file` anywhere
- [ ] `build` recipe body byte-identical to pre-change state
- [ ] All recipe lines tab-indented
- [ ] `make --dry-run create-dev` and `make --dry-run build` both exit 0
- [ ] Only `Makefile` modified in working tree (prior boulder's staged files untouched)
- [ ] All evidence files captured in `.omo/evidence/`
- [ ] F1-F4 all APPROVE
- [ ] User has given explicit okay
- [ ] NO commit made by executor
