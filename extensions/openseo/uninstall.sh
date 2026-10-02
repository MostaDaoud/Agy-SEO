#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills/seo-openseo"
MCP_CONFIG_FILE="${HOME}/.claude.json"
GEMINI_MCP_CONFIG="${HOME}/.gemini/config/mcp_config.json"

echo "Uninstalling OpenSEO extension..."
rm -rf "${SKILL_DIR}"

python3 - "${MCP_CONFIG_FILE}" "${GEMINI_MCP_CONFIG}" <<'PYEOF'
import json, os, sys, tempfile

def remove_from_file(filepath):
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        return
    mcp = data.get('mcpServers', {})
    if 'openseo' in mcp:
        del mcp['openseo']
        dirname = os.path.dirname(filepath) or '.'
        fd, tmp = tempfile.mkstemp(dir=dirname, prefix='.mcp_tmp.', suffix='.json')
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, filepath)
        print(f"v Removed openseo from {filepath}")

for path in sys.argv[1:]:
    remove_from_file(path)
PYEOF

echo "Done. OpenSEO extension uninstalled."
