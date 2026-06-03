# pyproject.toml Setup for paraview_mcp

## TL;DR

> **Quick Summary**: Create a proper `pyproject.toml` for the paraview_mcp repo, register a `paraview_mcp` console script entry point, fix a non-relative import that blocks the entry point, and surgically refresh `README.md` install instructions plus `AGENTS.md` to reflect the new state.
>
> **Deliverables**:
>
> - `pyproject.toml` (new) — hatchling build, BSD-3-Clause license, console script `paraview_mcp = paraview_mcp.main:main`
> - `paraview_mcp/main.py` — single-line import fix on line 23
> - `README.md` — surgical edit: install block + Claude Desktop config snippet
> - `AGENTS.md` — replace stale "import quirk" and "broken Makefile" sections with accurate post-change docs
>
> **Estimated Effort**: Short
> **Parallel Execution**: YES — 2 waves
> **Critical Path**: Task 1 (pyproject.toml) → Task 2 (import fix) → Wave 2 (docs + verification)

---

## Context

### Original Request

Create a proper `pyproject.toml` for the paraview_mcp repo. Generate a console script `paraview_mcp` that calls `main:main`. Declare the BSD-3-Clause license. Point GitHub and issue tracker URLs to NicholasSynovic/paraview_mcp (the user's fork). Mirror the structural layout of the reference pyproject at https://raw.githubusercontent.com/NicholasSynovic/dnn-resue-in-science/refs/heads/main/pyproject.toml.

### Interview Summary

**Key Discussions**:

- Distribution name: chose hyphenated `paraview-mcp` (PyPI-idiomatic). Package import remains `paraview_mcp`. Requires explicit `[tool.hatch.build.targets.wheel] packages = ["paraview_mcp"]`.
- License: BSD-3-Clause, verified in `LICENSE` line 1.
- URLs: user explicitly chose own fork (`NicholasSynovic/paraview_mcp`), not LLNL upstream.
- Console script name: `paraview_mcp` (underscore, matches package name).
- Import fix strategy: clean absolute import. Trade-off accepted: `python paraview_mcp/main.py` requires `pip install -e .` first; AGENTS.md will document this.
- README scope: surgical — install block + Claude Desktop config snippet only.
- httpx version: unpinned, mirroring `requirements.txt`.

**Research Findings**:

- `main.py:608` has `def main():` and `main.py:649` has `if __name__ == "__main__": main()`. Console script entry `paraview_mcp.main:main` will resolve correctly post-fix.
- `main.py:52` calls `pv_manager = ParaViewManager()` at module level — importing the module triggers a ParaView connection. Pre-existing; out of scope.
- `main.py:629-630` appends `--paraview_package_path` to `sys.path` inside `main()`, but the import at line 23 happens at module level (before `main()` runs). The flag is therefore a pre-existing no-op for the `paraview.simple` import. Out of scope.
- `paraview_manager.py` uses `from paraview.simple import *` intentionally (documented in AGENTS.md). Out of scope.
- `requirements.txt`: `httpx`, `mcp[cli]==1.9.4`. The `mcp` pin is intentional per git commit `916880c`.
- LICENSE: BSD 3-Clause, Copyright (c) 2018, Lawrence Livermore National Security, LLC.
- README authorship: Shusen Liu (liu42@llnl.gov) and Haichao Miao (miao1@llnl.gov).
- Repo has no `pyproject.toml` currently; it was removed in commit `b6be483`.
- Makefile uses `uv build`/`uv sync`/`uv version`; presence of `pyproject.toml` will unblock those targets but the user did not ask to verify the Makefile.

### Metis Review

**Identified Gaps** (addressed):

- Import-fix invocation-break risk → user chose clean absolute import; AGENTS.md will document the new invocation requirement.
- README scope ambiguity → user chose surgical scope.
- httpx pin ambiguity → user chose unpinned.
- Missing description string → added: `"MCP server exposing ParaView operations as tools for LLM-driven visualization"`.
- Missing Development Status → added `Development Status :: 3 - Alpha`.
- Missing authors decision → use original LLNL authors per README.
- Hatchling auto-discovery risk → explicit `[tool.hatch.build.targets.wheel] packages = ["paraview_mcp"]` directive mandatory.
- AGENTS.md sections should be REPLACED with accurate post-change docs, not deleted.

---

## Work Objectives

### Core Objective

Make `paraview_mcp` a properly packaged Python project: installable via `pip install -e .`, exposing a `paraview_mcp` console script that invokes `main()`, with BSD-3-Clause licensing declared, URLs pointing to NicholasSynovic/paraview_mcp, and documentation updated to reflect the new state.

### Concrete Deliverables

- `/home/nicholas/Documents/projects/paraview_mcp/pyproject.toml` (new file)
- `/home/nicholas/Documents/projects/paraview_mcp/paraview_mcp/main.py` (1-line edit on line 23)
- `/home/nicholas/Documents/projects/paraview_mcp/README.md` (install block + Claude Desktop snippet only)
- `/home/nicholas/Documents/projects/paraview_mcp/AGENTS.md` (replace stale sections)

### Definition of Done

> **Verification scope** — `paraview.simple` is conda-only and not present in CI/build envs. Verification stops at static + import-time checks. Runtime entry-point exercise (`pip install -e .` + `paraview_mcp --help`) requires a conda env with ParaView and is therefore an OPTIONAL bonus check, NOT a gate.

**Mandatory (gating) — must all pass:**

- [ ] `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` → exit 0
- [ ] `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['project']['scripts']['paraview_mcp']=='paraview_mcp.main:main'"` → exit 0 (console script wired correctly per static check)
- [ ] `python -m py_compile paraview_mcp/main.py` → exit 0
- [ ] `grep -n "from paraview_manager import ParaViewManager" paraview_mcp/main.py` → zero matches
- [ ] `grep -n "^from paraview_mcp.paraview_manager import ParaViewManager$" paraview_mcp/main.py` → exactly 1 match
- [ ] `grep -n "paraview_mcp_server.py" README.md` → zero matches in install/Claude config sections
- [ ] `python -m build --wheel --no-isolation` succeeds AND `unzip -l dist/paraview_mcp-0.1.0-py3-none-any.whl` shows both `paraview_mcp/main.py` and `paraview_mcp/paraview_manager.py` — if `build` is not installed, this becomes OPTIONAL
- [ ] AGENTS.md "import quirk" section reflects the new absolute-import behavior

**Optional (bonus — only run if conda ParaView env is available):**

- [ ] `pip install -e .` from clean conda+paraview env → succeeds
- [ ] `which paraview_mcp` → returns a non-empty path
- [ ] `paraview_mcp --help` → prints argparse usage (NOTE: module-level `pv_manager = ParaViewManager()` at main.py:52 runs BEFORE argparse; this check verifies the entry point is wired AND the ParaView connection succeeds. May fail at connection step in environments without a running pvserver — both outcomes are non-gating)

### Must Have

- `pyproject.toml` at repo root, syntactically valid TOML
- `[project] name = "paraview-mcp"`, `version = "0.1.0"`, `requires-python = ">=3.10"`
- `[project] license = "BSD-3-Clause"` (SPDX expression form)
- `[project.scripts] paraview_mcp = "paraview_mcp.main:main"`
- `[project.urls]` Homepage and Repository → `https://github.com/NicholasSynovic/paraview_mcp`
- `[build-system] requires = ["hatchling"]`, `build-backend = "hatchling.build"`
- `[tool.hatch.build.targets.wheel] packages = ["paraview_mcp"]` (mandatory because dist-name `paraview-mcp` ≠ package-dir `paraview_mcp`)
- `[tool.black] line-length = 79` (mirrors reference template structure, cosmetically faithful)
- Dependencies: `httpx`, `mcp[cli]==1.9.4` (preserve exact pin with `[cli]` extras bracket)
- Authors: Shusen Liu, Haichao Miao (per README)
- Description: `"MCP server exposing ParaView operations as tools for LLM-driven visualization"`
- Classifiers: `Development Status :: 3 - Alpha`, `License :: OSI Approved :: BSD License`, Python 3.10/3.11/3.12
- Keywords: `paraview`, `mcp`, `visualization`, `llm`, `scientific-visualization`
- Inline comment in pyproject.toml explaining why `paraview` is omitted from dependencies
- `paraview_mcp/main.py` line 23: `from paraview_mcp.paraview_manager import ParaViewManager`
- README install section mentions `pip install -e .` (after conda paraview prerequisite)
- README Claude Desktop config snippet uses console script `paraview_mcp`
- AGENTS.md "import quirk" section REPLACED (not deleted) to document new behavior
- AGENTS.md "Build / dev tooling — broken state" section REPLACED to note Makefile now works

### Must NOT Have (Guardrails)

- MUST NOT add `paraview` to `[project] dependencies` (conda-only, never pip-installable)
- MUST NOT touch `paraview_mcp/paraview_manager.py` (the `from paraview.simple import *` star import is intentional)
- MUST NOT touch `paraview_mcp/__init__.py` (must remain empty)
- MUST NOT add `[tool.ruff]`, `[tool.isort]`, or `[tool.bandit]` to pyproject.toml (pre-commit hooks already configured)
- MUST NOT run `uv sync`, `uv build`, or any `make` target during the task
- MUST NOT modify `Makefile`
- MUST NOT modify `requirements.txt` (kept as alternative install path)
- MUST NOT modify `.python-version`, `.pre-commit-config.yaml`, or any other config files
- MUST NOT rewrite README sections beyond install block and Claude Desktop config snippet (no touching: title, demo links, video, running instructions, citation, troubleshooting)
- MUST NOT add `__all__`, exports, or any code to `paraview_mcp/__init__.py`
- MUST NOT use the compat shim (try/except ImportError) — user chose clean absolute import
- MUST NOT generate or commit a `uv.lock` file
- MUST NOT remove the `mcp[cli]` extras bracket — `mcp==1.9.4` and `mcp[cli]==1.9.4` install different things
- MUST NOT change `httpx` to a pinned/floor version — user chose unpinned

### Spec Framework Integration

- **Detected Framework**: None
- **Notes**: No `openspec/` or `.specify/` directory in this repo. Standard plan execution applies.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision

- **Infrastructure exists**: NO (no test framework, no test dir)
- **Automated tests**: NONE (user did not request)
- **Framework**: N/A
- **Verification approach**: Agent-executed shell QA only. Each task has concrete commands with binary pass/fail.

### QA Policy

Every task includes agent-executed QA scenarios. Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **TOML/Config**: `python -c "import tomllib; ..."` + AST checks
- **Build**: `python -m build` + `unzip -l` to inspect wheel contents
- **Install**: `pip install -e .` in isolated venv
- **Entry point**: `which paraview_mcp` + `paraview_mcp --help`
- **Source edits**: `grep -n` and AST inspection for exact-match assertions
- **Documentation**: `grep -n` for presence/absence of expected strings

### Pre-existing Issues NOT to Fix (Out of Scope)

- `--paraview_package_path` flag is a no-op for the module-level `paraview.simple` import (sys.path append runs after import). Pre-existing, out of scope.
- `pv_manager = ParaViewManager()` at module level triggers ParaView connection on import. Pre-existing, out of scope.
- README has additional stale spots (wrong `python pvserver`, missing/incorrect conda command). User chose surgical scope — leave alone.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — start immediately, fully parallel):
├── Task 1: Create pyproject.toml at repo root [quick]
└── Task 2: Fix import in paraview_mcp/main.py line 23 [quick]

Wave 2 (Docs — after Wave 1):
├── Task 3: Surgical README.md edit (install + Claude config) [writing]
└── Task 4: Replace stale AGENTS.md sections [writing]

Wave FINAL (after ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay

Critical Path: Task 1 → Wave 2 → Final Wave → user okay
Parallel Speedup: ~50% (each wave runs concurrently)
Max Concurrent: 2 per wave (4 in final review)
```

### Dependency Matrix

- **Task 1** (pyproject.toml): no deps — start immediately. Blocks: F1, F2, F3.
- **Task 2** (main.py import): no deps — start immediately. Blocks: F1, F2, F3.
- **Task 3** (README): depends on Task 1 (so install command is correct). Blocks: F1, F4.
- **Task 4** (AGENTS.md): depends on Tasks 1 & 2 (so post-change docs are accurate). Blocks: F1, F4.
- **F1-F4**: depend on all of Tasks 1-4 complete.

### Agent Dispatch Summary

- **Wave 1** (2 tasks): T1 → `quick`, T2 → `quick`
- **Wave 2** (2 tasks): T3 → `writing`, T4 → `writing`
- **Wave FINAL** (4 tasks): F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x]   1. Create `pyproject.toml` at repo root mirroring reference template structure

        **What to do**:
    - Create new file `/home/nicholas/Documents/projects/paraview_mcp/pyproject.toml`
    - Sections in order: `[project]`, `[project.urls]`, `[project.scripts]`, `[build-system]`, `[tool.hatch.build.targets.wheel]`, `[tool.black]`
    - `[project]` fields:
        - `name = "paraview-mcp"`
        - `version = "0.1.0"`
        - `description = "MCP server exposing ParaView operations as tools for LLM-driven visualization"`
        - `readme = "README.md"`
        - `requires-python = ">=3.10"`
        - `license = "BSD-3-Clause"` (SPDX expression form, PEP 639)
        - `authors = [{name = "Shusen Liu", email = "liu42@llnl.gov"}, {name = "Haichao Miao", email = "miao1@llnl.gov"}]`
        - `keywords = ["paraview", "mcp", "visualization", "llm", "scientific-visualization"]`
        - `classifiers = ["Development Status :: 3 - Alpha", "License :: OSI Approved :: BSD License", "Programming Language :: Python :: 3", "Programming Language :: Python :: 3.10", "Programming Language :: Python :: 3.11", "Programming Language :: Python :: 3.12", "Topic :: Scientific/Engineering :: Visualization"]`
        - `dependencies = ["httpx", "mcp[cli]==1.9.4"]`
        - Add inline comment ABOVE `dependencies` explaining: `# Note: 'paraview' is intentionally omitted — it is only installable via conda (conda-forge::paraview) and cannot be pip-installed.`
    - `[project.urls]`:
        - `Homepage = "https://github.com/NicholasSynovic/paraview_mcp"`
        - `Repository = "https://github.com/NicholasSynovic/paraview_mcp"`
        - `Issues = "https://github.com/NicholasSynovic/paraview_mcp/issues"`
    - `[project.scripts]`:
        - `paraview_mcp = "paraview_mcp.main:main"`
    - `[build-system]`:
        - `requires = ["hatchling"]`
        - `build-backend = "hatchling.build"`
    - `[tool.hatch.build.targets.wheel]`:
        - `packages = ["paraview_mcp"]`
    - `[tool.black]`:
        - `line-length = 79`

    **Must NOT do**:
    - Do NOT add `paraview` to dependencies
    - Do NOT change `mcp[cli]==1.9.4` to anything else (preserve `[cli]` extras + exact pin)
    - Do NOT add `httpx` version specifier (keep unpinned)
    - Do NOT add `[tool.ruff]`, `[tool.isort]`, `[tool.bandit]`, or any other tool configuration
    - Do NOT add `optional-dependencies` or `dev` extras
    - Do NOT add a license file reference (`license = {file = "LICENSE"}`) — use SPDX expression form

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Single static file creation with concrete spec, no ambiguity, completes in 1-2 tool calls.
    - **Skills**: none
        - No domain skill overlap; this is a plain TOML write.
    - **Skills Evaluated but Omitted**:
        - `customize-opencode`: omitted — this is the user's project, not opencode configuration.

    **Parallelization**:
    - **Can Run In Parallel**: YES
    - **Parallel Group**: Wave 1 (with Task 2)
    - **Blocks**: F1, F2, F3 (final review needs the file)
    - **Blocked By**: None — can start immediately

    **References**:

    **Pattern References** (existing code to follow):
    - Reference template at `https://raw.githubusercontent.com/NicholasSynovic/dnn-resue-in-science/refs/heads/main/pyproject.toml` — section order, hatchling build backend, `[tool.black] line-length = 79`. **Why it matters**: User explicitly asked the plan to mirror this template's structure.

    **API/Type References** (contracts to implement against):
    - PEP 621 — `[project]` table specification. **Why it matters**: Defines the standard `[project]` metadata fields.
    - PEP 639 — license SPDX expression form. **Why it matters**: `license = "BSD-3-Clause"` is the modern form; avoid the deprecated `{file = "LICENSE"}` form.
    - PEP 508 — dependency specifier syntax. **Why it matters**: `mcp[cli]==1.9.4` is valid PEP 508 with extras.

    **Source-of-Truth References** (project-internal):
    - `/home/nicholas/Documents/projects/paraview_mcp/LICENSE` line 1: `"BSD 3-Clause License"` — confirms SPDX identifier `BSD-3-Clause`.
    - `/home/nicholas/Documents/projects/paraview_mcp/requirements.txt`: source of truth for the two dependencies and exact `mcp` pin.
    - `/home/nicholas/Documents/projects/paraview_mcp/README.md` — source of truth for authors (Liu, Miao @ LLNL).

    **External References**:
    - hatchling packages directive docs: `https://hatch.pypa.io/latest/config/build/#packages` — explains the `[tool.hatch.build.targets.wheel] packages` field. **Why it matters**: Mandatory because dist-name `paraview-mcp` ≠ package-dir `paraview_mcp`; without this, hatchling discovery may fail or behave version-dependently.

    **Acceptance Criteria**:

    **QA Scenarios (MANDATORY):**

    ```
    Scenario: pyproject.toml is syntactically valid TOML
      Tool: Bash
      Preconditions: file `/home/nicholas/Documents/projects/paraview_mcp/pyproject.toml` exists post-write
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && python -c "import tomllib; data = tomllib.load(open('pyproject.toml','rb')); print(data['project']['name'], data['project']['version'])"`
        2. Assert exit code == 0
        3. Assert stdout contains `paraview-mcp 0.1.0`
      Expected Result: Exit 0, stdout exactly `paraview-mcp 0.1.0\n`
      Failure Indicators: Non-zero exit (syntax error), missing fields, wrong values
      Evidence: .omo/evidence/task-1-toml-syntax.txt (capture stdout+stderr)

    Scenario: All required project fields present with exact expected values
      Tool: Bash
      Preconditions: pyproject.toml exists
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && python -c "
    import tomllib
    d = tomllib.load(open('pyproject.toml','rb'))
    p = d['project']
    assert p['name'] == 'paraview-mcp', p['name']
    assert p['version'] == '0.1.0', p['version']
    assert p['requires-python'] == '>=3.10', p['requires-python']
    assert p['license'] == 'BSD-3-Clause', p['license']
    assert p['readme'] == 'README.md', p['readme']
    assert 'mcp[cli]==1.9.4' in p['dependencies'], p['dependencies']
    assert 'httpx' in p['dependencies'], p['dependencies']
    assert d['project']['scripts']['paraview_mcp'] == 'paraview_mcp.main:main'
    assert d['project']['urls']['Repository'] == 'https://github.com/NicholasSynovic/paraview_mcp'
    assert d['build-system']['build-backend'] == 'hatchling.build'
    assert d['tool']['hatch']['build']['targets']['wheel']['packages'] == ['paraview_mcp']
    assert d['tool']['black']['line-length'] == 79
    print('OK')
    "`
        2. Assert exit 0
        3. Assert stdout contains `OK`
      Expected Result: Exit 0, stdout exactly `OK\n`
      Failure Indicators: AssertionError on any field, missing key
      Evidence: .omo/evidence/task-1-field-verification.txt

    Scenario: paraview is NOT in dependencies (negative guardrail check)
      Tool: Bash
      Preconditions: pyproject.toml exists
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && python -c "
    import tomllib
    deps = tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']
    for d in deps:
      assert not d.lower().startswith('paraview'), f'FAIL: paraview found in deps: {d}'
    print('paraview not in deps - OK')
    "`
        2. Assert exit 0
        3. Assert stdout contains `paraview not in deps - OK`
      Expected Result: Exit 0, success message
      Failure Indicators: AssertionError indicating paraview was added
      Evidence: .omo/evidence/task-1-no-paraview-dep.txt
    ```

    **Evidence to Capture:**
    - [ ] `.omo/evidence/task-1-toml-syntax.txt`
    - [ ] `.omo/evidence/task-1-field-verification.txt`
    - [ ] `.omo/evidence/task-1-no-paraview-dep.txt`

    **Commit**: YES (groups with 2, 3, 4 — single commit at end)
    - Message: `build: add pyproject.toml with console script entry point`
    - Files: `pyproject.toml`
    - Pre-commit: `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`

- [x]   2. Fix non-relative import in `paraview_mcp/main.py` line 23

        **What to do**:
    - Open `/home/nicholas/Documents/projects/paraview_mcp/paraview_mcp/main.py`
    - Locate line 23 containing: `from paraview_manager import ParaViewManager`
    - Replace with: `from paraview_mcp.paraview_manager import ParaViewManager`
    - Save file. No other edits to this file.

    **Must NOT do**:
    - Do NOT use the compat shim (try/except ImportError) — user explicitly chose clean absolute import
    - Do NOT touch any other line in main.py
    - Do NOT touch `paraview_manager.py` (out of scope)
    - Do NOT touch `__init__.py` (must remain empty)
    - Do NOT add `from __future__` imports
    - Do NOT reorder imports
    - Do NOT add `__all__`
    - Do NOT modify the `--paraview_package_path` sys.path append logic (pre-existing bug, out of scope)
    - Do NOT modify the module-level `pv_manager = ParaViewManager()` instantiation (pre-existing, out of scope)

    **Recommended Agent Profile**:
    - **Category**: `quick`
        - Reason: Single-line edit with exact-match string, no ambiguity, completes in 1-2 tool calls.
    - **Skills**: none
    - **Skills Evaluated but Omitted**:
        - `customize-opencode`: omitted — application code edit, not opencode config.

    **Parallelization**:
    - **Can Run In Parallel**: YES
    - **Parallel Group**: Wave 1 (with Task 1)
    - **Blocks**: F1, F2, F3, Task 4 (AGENTS.md update describes the new state)
    - **Blocked By**: None — can start immediately

    **References**:

    **Pattern References** (existing code to follow):
    - `/home/nicholas/Documents/projects/paraview_mcp/paraview_mcp/main.py` line 23 — current line: `from paraview_manager import ParaViewManager`. **Why it matters**: This is the exact-match line to edit. Verify it exists on line 23 (line number may have shifted; the exact string is the source of truth).

    **API/Type References** (contracts to implement against):
    - PEP 328 — absolute import semantics. **Why it matters**: `from paraview_mcp.paraview_manager` requires `paraview_mcp` to be discoverable on `sys.path`, which happens only after `pip install -e .`.

    **Source-of-Truth References**:
    - `/home/nicholas/Documents/projects/paraview_mcp/AGENTS.md` "Import quirk" section — explains pre-fix behavior. After this task, AGENTS.md must be updated (Task 4).

    **Acceptance Criteria**:

    **QA Scenarios (MANDATORY):**

    ```
    Scenario: Old import is gone, new import is present
      Tool: Bash
      Preconditions: main.py edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && grep -c '^from paraview_manager import ParaViewManager$' paraview_mcp/main.py`
        2. Assert output is `0` (old import absent)
        3. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && grep -c '^from paraview_mcp.paraview_manager import ParaViewManager$' paraview_mcp/main.py`
        4. Assert output is `1` (new import present, exactly once)
      Expected Result: First grep returns 0, second grep returns 1
      Failure Indicators: Old import still present, new import missing, or duplicated
      Evidence: .omo/evidence/task-2-import-grep.txt

    Scenario: AST confirms the correct module path
      Tool: Bash
      Preconditions: main.py edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && python -c "
    import ast
    tree = ast.parse(open('paraview_mcp/main.py').read())
    hits = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module and 'paraview_manager' in n.module]
    assert len(hits) == 1, f'expected 1 hit, got {len(hits)}'
    assert hits[0].module == 'paraview_mcp.paraview_manager', hits[0].module
    print('AST OK:', hits[0].module)
    "`
        2. Assert exit 0
        3. Assert stdout contains `AST OK: paraview_mcp.paraview_manager`
      Expected Result: Exit 0 with confirmation message
      Failure Indicators: Wrong module string, multiple imports, AST parse error
      Evidence: .omo/evidence/task-2-ast-check.txt

    Scenario: File is still syntactically valid Python
      Tool: Bash
      Preconditions: main.py edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && python -m py_compile paraview_mcp/main.py`
        2. Assert exit 0 (compiles even without paraview installed — module-level instantiation only fails at import-execution time, not at compile time)
      Expected Result: Exit 0
      Failure Indicators: SyntaxError
      Evidence: .omo/evidence/task-2-py-compile.txt
    ```

    **Evidence to Capture:**
    - [ ] `.omo/evidence/task-2-import-grep.txt`
    - [ ] `.omo/evidence/task-2-ast-check.txt`
    - [ ] `.omo/evidence/task-2-py-compile.txt`

    **Commit**: YES (groups with 1, 3, 4)
    - Message: included in combined commit at end
    - Files: `paraview_mcp/main.py`
    - Pre-commit: `python -m py_compile paraview_mcp/main.py`

- [x]   3. Surgically update `README.md` install section and Claude Desktop config snippet

    **What to do**:
    - Open `/home/nicholas/Documents/projects/paraview_mcp/README.md`
    - Locate the installation section. Add (do not replace) a clearly-labeled note that after installing `paraview` via conda, the package can be installed with: `pip install -e .` from the repo root, which registers the `paraview_mcp` console script.
    - Locate the Claude Desktop config JSON snippet. Update it so the `command` field invokes the console script `paraview_mcp` (use `paraview_mcp` as the command — must be on PATH within the conda env — and remove the `args` array entry pointing at the stale `paraview_mcp_server.py` path). This MUST be the chosen form to honor the Must-Have requirement that the snippet use the console script. Do NOT fall back to `python -m paraview_mcp.main` or any other form.
    - Preserve the rest of the README verbatim. Do NOT touch: title, demo links, video embed, running instructions for `pvserver`, citation block, troubleshooting, contributors, or any other section.

    **Must NOT do**:
    - Do NOT fix the stale `python pvserver` → `pvserver` typo elsewhere in the README (out of scope per user's surgical choice)
    - Do NOT remove other stale `paraview_mcp_server.py` references outside the Claude Desktop config snippet (out of scope)
    - Do NOT rewrite the conda installation command for paraview
    - Do NOT add a CI badge, build status, or any new badges
    - Do NOT reformat or re-indent unrelated lines

    **Recommended Agent Profile**:
    - **Category**: `writing`
        - Reason: Targeted documentation edit requiring careful preservation of surrounding content. Domain is prose/markdown.
    - **Skills**: none
    - **Skills Evaluated but Omitted**:
        - `customize-opencode`: omitted — user's project documentation, not opencode config.

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Task 4)
    - **Parallel Group**: Wave 2 (with Task 4)
    - **Blocks**: F1, F4
    - **Blocked By**: Task 1 (README must accurately reflect the install command from pyproject.toml)

    **References**:

    **Pattern References**:
    - `/home/nicholas/Documents/projects/paraview_mcp/README.md` — current install section and Claude Desktop config snippet are the targets. **Why it matters**: must understand existing structure before editing.

    **Source-of-Truth References**:
    - Task 1 output (`pyproject.toml`): defines the console script name `paraview_mcp` and confirms editable install works via `pip install -e .`.

    **Acceptance Criteria**:

    **QA Scenarios (MANDATORY):**

    ````
    Scenario: README contains `pip install -e .` reference
      Tool: Bash
      Preconditions: README.md edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && grep -c 'pip install -e \.' README.md`
        2. Assert output is >= 1
      Expected Result: At least one occurrence of `pip install -e .`
      Failure Indicators: Zero occurrences (install instruction missing)
      Evidence: .omo/evidence/task-3-readme-install-grep.txt

    Scenario: Claude Desktop config snippet references `paraview_mcp` (console script) not stale `paraview_mcp_server.py`
      Tool: Bash
      Preconditions: README.md edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && awk '/claude_desktop_config/,/^```$/' README.md > /tmp/claude_snippet.txt 2>&1 || true`
        2. If extraction yields a snippet block, run: `grep -c 'paraview_mcp_server.py' /tmp/claude_snippet.txt` — assert output is `0`
        3. Run: `grep -c 'paraview_mcp' /tmp/claude_snippet.txt` — assert output is >= 1
      Expected Result: stale filename absent from snippet; new entry point present
      Failure Indicators: Stale `paraview_mcp_server.py` still in snippet
      Evidence: .omo/evidence/task-3-claude-snippet.txt

    Scenario: Sections outside install + Claude config block are unchanged
      Tool: Bash
      Preconditions: git status shows README.md modified
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && git diff README.md | grep -E '^[+-]' | grep -v '^[+-]{3}' > /tmp/readme-diff.txt`
        2. Manually inspect /tmp/readme-diff.txt — assert all `+` and `-` lines are within install block or Claude Desktop config snippet. Title line, demo links, video, citation, troubleshooting MUST NOT appear in diff.
        3. Run: `wc -l /tmp/readme-diff.txt` — assert line count is reasonable (< 30 lines of changes total, indicating surgical scope was respected)
      Expected Result: Diff is small and confined to two regions
      Failure Indicators: Diff touches title, citation, demo, or other sections (scope creep)
      Evidence: .omo/evidence/task-3-readme-diff.txt (capture the diff and a manual annotation noting which regions were touched)
    ````

    **Evidence to Capture:**
    - [ ] `.omo/evidence/task-3-readme-install-grep.txt`
    - [ ] `.omo/evidence/task-3-claude-snippet.txt`
    - [ ] `.omo/evidence/task-3-readme-diff.txt`

    **Commit**: YES (groups with 1, 2, 4)
    - Files: `README.md`

- [x]   4. Replace stale `AGENTS.md` sections with accurate post-change documentation

        **What to do**:
    - Open `/home/nicholas/Documents/projects/paraview_mcp/AGENTS.md`
    - Locate the section currently titled `## Build / dev tooling — broken state, read before touching` (or similar) discussing how `make build`/`uv build` fails because `pyproject.toml` is missing. REPLACE with an updated section noting that `pyproject.toml` now exists, `make build` and `uv sync` should work, and `pip install -e .` is the canonical install command.
    - Locate the section under `### Import quirk (will bite you)` (or similar) discussing how `python paraview_mcp/main.py` works but `python -m paraview_mcp.main` fails. REPLACE with an updated section explaining:
        - The import is now `from paraview_mcp.paraview_manager import ParaViewManager` (absolute)
        - The canonical run command is now the console script `paraview_mcp` (registered via `pip install -e .`)
        - `python paraview_mcp/main.py` no longer works standalone — it requires `pip install -e .` first
        - `python -m paraview_mcp.main` now works after install
    - Update the `## Running the server` section's example command from `python paraview_mcp/main.py --server localhost --port 11111` to the console script form: `paraview_mcp --server localhost --port 11111` (this is a minimal update, not a full rewrite).
    - Preserve all other sections verbatim: Layout, Environment & quirks, ParaView quirks, Lint/format/hooks, Adding or changing MCP tools, Git/branches.

    **Must NOT do**:
    - Do NOT delete the sections — REPLACE with updated content
    - Do NOT add new sections (no "CHANGELOG", no "Migration notes", etc.)
    - Do NOT change the file's overall structure or heading hierarchy
    - Do NOT touch the `Environment & quirks` section (still accurate)
    - Do NOT touch the `Adding or changing MCP tools` section (still accurate)
    - Do NOT touch the `Git / branches` section
    - Do NOT modify the `from paraview.simple import *` star import note (still accurate, still a guardrail)

    **Recommended Agent Profile**:
    - **Category**: `writing`
        - Reason: Documentation rewrite requiring careful preservation of accurate sections while replacing two specific outdated ones.
    - **Skills**: none

    **Parallelization**:
    - **Can Run In Parallel**: YES (with Task 3)
    - **Parallel Group**: Wave 2 (with Task 3)
    - **Blocks**: F1, F4
    - **Blocked By**: Tasks 1 & 2 (description of new state requires them to be done)

    **References**:

    **Pattern References**:
    - `/home/nicholas/Documents/projects/paraview_mcp/AGENTS.md` — current "Build / dev tooling" and "Import quirk" sections are the replacement targets. **Why it matters**: must understand existing prose tone before rewriting.

    **Source-of-Truth References**:
    - Task 1 output (pyproject.toml): defines new build system, console script
    - Task 2 output (main.py import fix): defines new import path

    **Acceptance Criteria**:

    **QA Scenarios (MANDATORY):**

    ```
    Scenario: Stale phrases removed from AGENTS.md
      Tool: Bash
      Preconditions: AGENTS.md edited
      Steps:
        1. Run: `cd /home/nicholas/Documents/projects/paraview_mcp && grep -c 'broken state' AGENTS.md` — assert 0
        2. Run: `grep -c 'make build.*fails' AGENTS.md` — assert 0
        3. Run: `grep -c 'ModuleNotFoundError.*paraview_mcp\.main' AGENTS.md` — assert 0 (old quirk text gone)
      Expected Result: All three grep counts are 0
      Failure Indicators: Stale text remains
      Evidence: .omo/evidence/task-4-agentsmd-stale-removed.txt

    Scenario: New accurate phrases present in AGENTS.md
      Tool: Bash
      Preconditions: AGENTS.md edited
      Steps:
        1. Run: `grep -c 'pip install -e \.' AGENTS.md` — assert >= 1
        2. Run: `grep -c 'paraview_mcp.paraview_manager' AGENTS.md` — assert >= 1 (new import documented)
        3. Run: `grep -c 'console script' AGENTS.md` — assert >= 1
      Expected Result: All three counts >= 1
      Failure Indicators: New documentation missing
      Evidence: .omo/evidence/task-4-agentsmd-new-content.txt

    Scenario: Preserved sections still intact
      Tool: Bash
      Preconditions: AGENTS.md edited
      Steps:
        1. Run: `grep -c 'from paraview.simple import \*' AGENTS.md` — assert >= 1 (star import note still present)
        2. Run: `grep -c 'paraview.simple.*only available' AGENTS.md` — assert >= 1 (Environment & quirks section preserved)
        3. Run: `grep -c '## Git' AGENTS.md` — assert >= 1 (Git section preserved)
      Expected Result: All preserved sections still present
      Failure Indicators: Accidental deletion of preserved content
      Evidence: .omo/evidence/task-4-agentsmd-preserved.txt

    Scenario: AGENTS.md is still well-formed markdown (no broken headings)
      Tool: Bash
      Preconditions: AGENTS.md edited
      Steps:
        1. Run: `python -c "
    import re
    content = open('/home/nicholas/Documents/projects/paraview_mcp/AGENTS.md').read()
    ```

# Check heading hierarchy: no jumps from H1 to H3 etc.

headings = re.findall(r'^(#+)\s', content, re.M)
levels = [len(h) for h in headings]
for i in range(1, len(levels)):
assert levels[i] - levels[i-1] <= 1, f'Heading jump at index {i}: {levels[i-1]} -> {levels[i]}'
print('Heading hierarchy OK')
"`      2. Assert exit 0
    Expected Result: Exit 0 with`Heading hierarchy OK`
Failure Indicators: AssertionError on heading levels
Evidence: .omo/evidence/task-4-agentsmd-headings.txt

```

**Evidence to Capture:**
- [ ] `.omo/evidence/task-4-agentsmd-stale-removed.txt`
- [ ] `.omo/evidence/task-4-agentsmd-new-content.txt`
- [ ] `.omo/evidence/task-4-agentsmd-preserved.txt`
- [ ] `.omo/evidence/task-4-agentsmd-headings.txt`

**Commit**: YES (groups with 1, 2, 3)
- Files: `AGENTS.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan compliance audit** — `oracle`
Read this plan end-to-end. For each "Must Have": verify implementation exists (read file, grep for value, run TOML loader). For each "Must NOT Have": grep codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.omo/evidence/` for Tasks 1-4. Verify pyproject.toml contains: name=paraview-mcp, version=0.1.0, requires-python>=3.10, license=BSD-3-Clause, console script paraview_mcp, URLs to NicholasSynovic/paraview_mcp, hatch packages directive, mcp[cli]==1.9.4 preserved, httpx unpinned, paraview absent. Verify main.py:23 has new absolute import and old import is gone. Verify README has `pip install -e .`. Verify AGENTS.md stale phrases removed and new phrases present.
Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code quality review** — `unspecified-high`
Run inside repo root in a fresh venv where possible. **Gating checks (must pass):**
  - `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` — TOML syntax
  - `python -m py_compile paraview_mcp/main.py` — Python syntax
  - `python -m build --wheel --no-isolation` if `build` is available, then `unzip -l dist/paraview_mcp-0.1.0-py3-none-any.whl` and confirm `paraview_mcp/main.py` + `paraview_mcp/paraview_manager.py` are in the wheel (SKIP allowed only if `build` not installable without network)
**Optional checks (bonus only — require a conda env with `paraview`; SKIP is acceptable, FAIL is non-gating):**
  - `pip install -e .` and `pip show paraview-mcp` — confirm Name and Version
  - `which paraview_mcp` — confirm script registered
  - `paraview_mcp --help 2>&1 | head -20` — module-level `pv_manager = ParaViewManager()` runs first; expect either argparse help OR a connection error from paraview, both acceptable
Review diffs for: AI slop, accidental scope creep into other files, removed-but-shouldn't-have content, accidental reformatting.
Output: `TOML [PASS/FAIL] | Compile [PASS/FAIL] | Wheel [PASS/FAIL/SKIP] | Install [PASS/FAIL/SKIP] | Script [PASS/FAIL/SKIP] | Help [PASS/FAIL/SKIP] | Files [N clean/N issues] | VERDICT (gating checks only)`

- [x] F3. **Real manual QA** — `unspecified-high`
Execute EVERY QA scenario from EVERY task (Tasks 1-4) — follow exact steps, capture evidence to `.omo/evidence/final-qa/`. Re-run all grep/static checks. **Gating integration check**: confirm `python -c "import tomllib; ..."` + `python -m py_compile paraview_mcp/main.py` both pass after all tasks land — these are environment-independent. **Optional runtime integration check** (SKIP if no conda+paraview env): `pip install -e .` end-to-end, `which paraview_mcp`. **Static edge case**: `grep -c "from paraview_manager import ParaViewManager" paraview_mcp/main.py` returns 0 (old import gone, confirming the absolute-import refactor — `python paraview_mcp/main.py` will now fail at the import line per user's "clean absolute import" choice; this static check is sufficient evidence, no runtime invocation needed).
Output: `Scenarios [N/N pass] | Static Integration [PASS/FAIL] | Runtime Integration [PASS/FAIL/SKIP] | Edge Cases [N tested] | VERDICT (gating only)`

- [x] F4. **Scope fidelity check** — `deep`
For each task: read "What to do", read actual git diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Specifically check:
  - `paraview_mcp/__init__.py` unchanged (still empty)
  - `paraview_mcp/paraview_manager.py` unchanged
  - `Makefile` unchanged
  - `requirements.txt` unchanged
  - `.python-version`, `.pre-commit-config.yaml`, `LICENSE`, `NOTICE` unchanged
  - README diff confined to install block + Claude Desktop config snippet
  - AGENTS.md diff confined to "Build / dev tooling" and "Import quirk" sections plus the one-line `## Running the server` example update
  - No new files except `pyproject.toml`
Run: `git status --porcelain` and assert only the 4 expected files appear (plus any opencode-internal files like .omo/).
Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

> **BLOCKED**: GPG signing fails in non-interactive session (`commit.gpgsign=true`, key `56369568A84C28C14F2800E34C471E45EAACD88D`). Files are staged and ready. User must run the commit in a terminal where their GPG agent is unlocked, OR run `git commit --no-gpg-sign` to bypass.

Single combined commit at the end of all 4 tasks (atomic change — all four files are part of the same logical unit):

- Message:
```

build: add pyproject.toml with paraview_mcp console script

- New pyproject.toml: hatchling build, BSD-3-Clause, paraview-mcp 0.1.0
- Console script `paraview_mcp = paraview_mcp.main:main` registered
- Fix non-relative import in main.py to enable entry point
- Surgical README update: install via `pip install -e .`, Claude config snippet
- AGENTS.md: replace stale "broken Makefile" and "import quirk" sections

Note: `paraview` deliberately omitted from dependencies (conda-only).

````
- Files: `pyproject.toml`, `paraview_mcp/main.py`, `README.md`, `AGENTS.md`
- Pre-commit: `pre-commit run --all-files` (will run ruff-format, ruff-check, isort, bandit on touched .py file)

---

## Success Criteria

### Verification Commands

**Gating (must all pass — environment-independent):**
```bash
# TOML valid
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"  # Expected: exit 0

# Field check
python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['project']['name']=='paraview-mcp'; assert d['project']['license']=='BSD-3-Clause'; assert d['project']['scripts']['paraview_mcp']=='paraview_mcp.main:main'; print('OK')"  # Expected: OK

# Import fix (static)
grep -c '^from paraview_manager import ParaViewManager$' paraview_mcp/main.py  # Expected: 0
grep -c '^from paraview_mcp.paraview_manager import ParaViewManager$' paraview_mcp/main.py  # Expected: 1

# Python syntax
python -m py_compile paraview_mcp/main.py  # Expected: exit 0

# Guardrails
python -c "import tomllib; deps=tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']; assert not any(d.lower().startswith('paraview') for d in deps), deps; print('paraview not in deps')"  # Expected: paraview not in deps

# Out-of-scope files unchanged
git diff --stat paraview_mcp/__init__.py paraview_mcp/paraview_manager.py Makefile requirements.txt LICENSE NOTICE .python-version .pre-commit-config.yaml  # Expected: empty
````

**Optional bonus (only if conda+paraview env available — SKIP is acceptable):**

```bash
# Install + entry point (requires paraview installed via conda)
pip install -e . && which paraview_mcp  # Expected: non-empty path

# Entry point fires (NOTE: module-level pv_manager=ParaViewManager() at main.py:52 runs before argparse;
# may print argparse help OR fail at ParaView connection step — both acceptable)
paraview_mcp --help 2>&1 | head -3
```

### Final Checklist

- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All 4 tasks completed
- [ ] All F1-F4 reviews APPROVE
- [ ] User has given explicit "okay" before marking work complete
