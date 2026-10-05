# Plan Gate Extension for Agy-SEO

Plan-first execution gate for technical SEO, scripting, and code automation. Restricts the model to read-only discovery (`Read`, `Grep`, `Glob`) until an orchestrator-approved plan is signed off.

Based on [AgriciDaniel/plan-gate](https://github.com/AgriciDaniel/plan-gate).

## Why Plan Gate?

When models are given unrestricted write tools, they frequently jump straight into editing files before understanding dependencies, creating subtle regressions or compounding mistakes.

Plan Gate enforces a strict two-phase separation of concerns:

1. **Phase 1: Read-Only Plan Formation (Planner)**
   - Model is physically restricted to `Read`, `Grep`, and `Glob`.
   - Cannot mutate files (`Write`, `Edit`, `Bash` are completely disabled).
   - Produces a machine-readable plan matching `references/plan-schema.md` with explicit `open_questions` and `wrongness` criteria.

2. **Phase 2: Orchestrator Review & Approval**
   - The orchestrator or human reviews the plan, answers all open questions, and approves or rejects.

3. **Phase 3: Execution (Executor)**
   - A fresh executor subagent or thread receives the approved plan as its explicit contract and applies changes.

4. **Phase 4: Ground-Truth Verification**
   - Verification runs independent tests to confirm correctness.

## Two Execution Lanes

- **Lane A (Claude Subagent):** Uses the dedicated `seo-plan-gate-planner` subagent with a locked read-only tool allowlist (`Read`, `Grep`, `Glob`).
- **Lane B (Codex Sandbox):** Runs Codex in a bubblewrap read-only sandbox without the `--write` flag for the planning pass.

## Installation

### Unix / macOS
```bash
./extensions/plan-gate/install.sh
```

### Windows (PowerShell)
```powershell
.\extensions\plan-gate\install.ps1
```

## Quick Start

```
/seo plan-gate <task description>
```

Subcommands:
- `/seo plan-gate claude`: Run Lane A with the `seo-plan-gate-planner` agent.
- `/seo plan-gate codex`: Run Lane B with Codex read-only pass.
- `/seo plan-gate preflight`: Test environment preconditions for Lane B sandbox.
- `/seo plan-gate audit`: Verify Lane A tool allowlist has not regressed.
