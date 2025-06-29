


# Spec: Automated Spec-to-Production Software Development System

## Purpose

Automate the end-to-end software development process—from initial product idea through production deployment—by tightly coupling a stepwise playbook, a living specification, and an LLM agent capable of reasoning, code generation, test writing, and incremental learning. The system aims to maximize engineering velocity, reduce mistakes, and produce an auditable, continuously improving trail of engineering decisions.

---

## Core Components

1. **Living Specification (/docs/spec.md)**
   - Single source of truth for requirements, interfaces, invariants, and open questions.
   - Versioned with a content hash, referenced in every relevant commit.
   - Amended only via an explicit “spec amendment” process with reason logging.

2. **Playbook & Progress Beacon**
   - Machine-readable `playbook.yml` defines each phase (e.g. Spec Draft, E2E Test, Scaffold, Domain Logic, Infra Integration, Perf Budget, Done).
   - Current progress tracked by file (`progress.json`), git tag, or commit prefix.
   - Only one active step at a time; advancement gated by CI and step-specific exit conditions.

3. **Atomic, Always-Green Commits**
   - Each commit addresses a single playbook step and only advances when all relevant tests pass.
   - Commits are conventionally formatted, include spec hash and progress step, and log reasoning for the change.
   - Pre-commit and pre-push hooks enforce discipline and validate all constraints.

4. **LLM Agent (Bot)**
   - Reads the current spec, playbook step, and repo context.
   - Generates stubs, interfaces, tests, and real implementations as dictated by the current playbook step.
   - Proposes spec amendments with clear reasoning when implementation diverges from the spec or new requirements emerge.
   - Tracks and logs all actions, decisions, and justifications.

5. **CI/CD Integration**
   - CI enforces exit conditions for each playbook step.
   - Blocks progress or code merge if tests are failing, coverage is inadequate, mutation score drops, or progress beacon is out of sync.

6. **Reasoning Log & Architectural Decision Records (ADR)**
   - Every spec amendment and major design decision is logged (e.g. `/docs/adr/NNNN-why-X.md`), referencing the reason for change and its context.
   - This forms a historical, searchable trail of engineering intent.

7. **Continuous Model Fine-Tuning**
   - All commits, spec deltas, amendments, and test results are harvested as training data.
   - Nightly or streaming fine-tune jobs incrementally improve the LLM’s ability to operate within the playbook and reduce repeated mistakes.
   - Evaluated via an automated harness to prevent regressions.

---

## Workflow

### Progress.md
The file progress.md is updated after each step and tracks the progress of the implementation.
It has the following sections:
- "Step": that shows the current dev step, e.g., "A Preparation, step 3".
- "Details": that lists any required details for the step
- "Notes": that lists any relevant notes.

### A: preparation
1. Generate spec.md with product idea and requirements.
2. Generate progress.md with current state in preparation or refinement loop. File is updated after each step and may contain any additional info. When updating, outdated info is removed.
3. Generate basic runnable system mockup with interfaces.
4. Generate e2e test for mockup system.

### B: Refinement loop
Updates progress.md after each step
1. plan next refinement; ask user for feedback / adjustment
2. adjust e2e test according to plan
3. implement refinement including unit tests
4. check e2e test is passing and
    - fix implementation until it passes
    - or adjust e2e test
    - or abort (refinement failed -> plan has to change)
5. review spec and decide if a change is needed; if yes, make the change
6. commit changes
7. continue with 1 or stop if completed

---

## Invariants

- The spec is the only source of truth for requirements and contracts.
- No code or test is committed unless all relevant checks are green and commit metadata matches the current step and spec.
- All design/requirement changes are justified in writing and logged.
- The bot never skips steps; progress is only advanced by CI when exit conditions are satisfied.

---

## Open Questions / Extensibility

- How granular should the playbook steps be for your context (micro-commits vs. larger blocks)?
- What level of human review is required for spec amendments and at what steps is the process fully autonomous?
- Should LLM actions be signed/tagged distinctly from human ones for future analysis?
- What privacy/PII constraints are needed for harvesting training data?
