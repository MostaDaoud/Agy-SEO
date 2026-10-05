#!/usr/bin/env bash
# Uninstall the seo-plan-gate skill and planner agent from ~/.claude.
set -uo pipefail

DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

echo "seo-plan-gate uninstaller"

if [ -d "$DEST/skills/seo-plan-gate" ]; then
  rm -rf "$DEST/skills/seo-plan-gate"
  echo "Removed $DEST/skills/seo-plan-gate"
fi

if [ -f "$DEST/agents/seo-plan-gate-planner.md" ]; then
  rm -f "$DEST/agents/seo-plan-gate-planner.md"
  echo "Removed $DEST/agents/seo-plan-gate-planner.md"
fi

echo "Done. seo-plan-gate uninstalled."
