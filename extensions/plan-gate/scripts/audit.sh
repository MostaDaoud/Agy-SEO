#!/usr/bin/env bash
# Plan Gate: verify Lane A enforcement has not regressed.
# The tools: allowlist is the ONLY thing holding the gate under auto mode.
set -uo pipefail

AGENT="${1:-$(dirname "$0")/../agents/seo-plan-gate-planner.md}"
if [ ! -f "$AGENT" ]; then
  AGENT="$HOME/.claude/agents/seo-plan-gate-planner.md"
fi

python3 - "$AGENT" <<'PY'
import re, sys
p = sys.argv[1]
try:
    s = open(p, encoding="utf-8").read()
except OSError as e:
    print(f"FAIL  cannot read {p}: {e}"); sys.exit(1)

m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
if not m:
    print(f"FAIL  {p}: no YAML frontmatter"); sys.exit(1)
try:
    import yaml
    fm = yaml.safe_load(m.group(1))
except ImportError:
    # simple regex fallback if pyyaml not installed
    fm = {}
    lines = m.group(1).splitlines()
    in_tools = False
    tools_list = []
    for line in lines:
        if line.startswith("tools:"):
            in_tools = True
            continue
        if in_tools:
            if line.strip().startswith("-"):
                tools_list.append(line.strip().lstrip("-").strip())
            else:
                break
    fm["tools"] = tools_list

fail = 0
tools = fm.get("tools")

if tools is None:
    print("FAIL  no tools: allowlist. Agent inherits EVERY tool, gate is open.")
    fail = 1
else:
    mutating = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Bash"}
    found = sorted(mutating & set(tools))
    if found:
        print(f"FAIL  mutating tools present: {', '.join(found)}")
        fail = 1
    else:
        print(f"ok    tools allowlist read-only: {', '.join(tools)}")

print("\nLane A enforcement intact." if not fail else "\nLane A GATE IS OPEN. Fix before delegating.")
sys.exit(fail)
PY
