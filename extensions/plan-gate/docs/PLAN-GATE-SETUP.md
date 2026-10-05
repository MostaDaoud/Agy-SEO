# Plan Gate Setup & Operating Manual

## Overview

Plan Gate gates delegated technical SEO, programmatic scripts, and codebase changes behind an orchestrator-reviewed plan.

The core insight: Prompting a model "please plan first and do not write" frequently fails under autonomous modes. Plan Gate enforces the gate through capability restrictions, removing mutating tools completely during discovery.

## Installation

### Unix / macOS
```bash
chmod +x ./extensions/plan-gate/install.sh
./extensions/plan-gate/install.sh
```

### Windows (PowerShell)
```powershell
.\extensions\plan-gate\install.ps1
```

The installer:
1. Copies `skills/seo-plan-gate/` to `~/.claude/skills/seo-plan-gate/`.
2. Copies `agents/seo-plan-gate-planner.md` to `~/.claude/agents/seo-plan-gate-planner.md`.
3. Verifies that mutating tools (`Write`, `Edit`, `Bash`, etc.) are absent from the planner agent.

## Execution Lanes

### Lane A: Claude Subagent

Lane A is native to Claude Code. It invokes the `seo-plan-gate-planner` subagent, whose frontmatter specifies:
```yaml
tools:
  - Read
  - Grep
  - Glob
```

Because mutating tools are omitted from the allowlist, the model cannot edit files even if prompted or tempted to fix things inline.

**Workflow:**
1. Spawn planner:
   ```
   Agent(subagent_type: "seo-plan-gate-planner", prompt: "<task>\n\nReturn a plan matching references/plan-schema.md")
   ```
2. Review plan using `references/review-checklist.md`.
3. Answer all items in `open_questions`.
4. Persist plan to `plans/<date>-<slug>/plan.md` and decisions to `plans/<date>-<slug>/decisions.md`.
5. Spawn a fresh executor subagent with the approved plan.
6. Verify against tests and linters.

### Lane B: OpenAI Codex Companion

Lane B runs on an external Codex subscription inside a bubblewrap sandbox.

**Workflow:**
1. Run preflight check:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension plan-gate preflight.py
   ```
2. Run planning pass without `--write` (sandbox is strictly read-only).
3. Review plan and answer open questions.
4. Spawn a fresh thread with `--fresh --write` passing the approved plan text.

## Verification & Auditing

To audit that Lane A enforcement has not regressed:
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension plan-gate audit.py
```
Or via subcommand:
```
/seo plan-gate audit
```

## Uninstallation

### Unix / macOS
```bash
./extensions/plan-gate/uninstall.sh
```

### Windows (PowerShell)
```powershell
.\extensions\plan-gate\uninstall.ps1
```
