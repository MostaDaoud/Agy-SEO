#!/usr/bin/env python3
"""Plan Gate: verify Lane A enforcement has not regressed.
The tools: allowlist is the ONLY thing holding the gate under auto mode.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

def main() -> int:
    default_agent = Path(__file__).resolve().parent.parent / "agents" / "seo-plan-gate-planner.md"
    agent_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_agent
    if not agent_path.is_file():
        home_agent = Path.home() / ".claude" / "agents" / "seo-plan-gate-planner.md"
        if home_agent.is_file():
            agent_path = home_agent
        else:
            print(f"FAIL  cannot locate agent file at {agent_path}")
            return 1

    try:
        content = agent_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"FAIL  cannot read {agent_path}: {e}")
        return 1

    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        print(f"FAIL  {agent_path}: no YAML frontmatter")
        return 1

    frontmatter = match.group(1)
    tools_list = []
    in_tools = False
    for line in frontmatter.splitlines():
        if line.startswith("tools:"):
            in_tools = True
            rest = line[6:].strip()
            if rest:
                tools_list = [t.strip() for t in rest.split(",")]
                in_tools = False
            continue
        if in_tools:
            stripped = line.strip()
            if stripped.startswith("-"):
                tools_list.append(stripped.lstrip("-").strip())
            elif stripped:
                break

    if not tools_list:
        print("FAIL  no tools: allowlist. Agent inherits EVERY tool, gate is open.")
        return 1

    mutating = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Bash"}
    found = sorted(mutating & set(tools_list))
    if found:
        print(f"FAIL  mutating tools present: {', '.join(found)}")
        print("\nLane A GATE IS OPEN. Fix before delegating.")
        return 1

    print(f"ok    tools allowlist read-only: {', '.join(tools_list)}")
    print("\nLane A enforcement intact.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
