#!/usr/bin/env bash
set -euo pipefail

main() {
    SKILL_DIR="${HOME}/.claude/skills/seo-openseo"
    SEO_SKILL_DIR="${HOME}/.claude/skills/seo"
    MCP_CONFIG_FILE="${HOME}/.claude.json"
    GEMINI_MCP_CONFIG="${HOME}/.gemini/config/mcp_config.json"

    echo "===================================="
    echo "  OpenSEO Extension - Installer"
    echo "  For Agy-SEO & Claude SEO"
    echo "===================================="
    echo ""

    if [ ! -d "${SEO_SKILL_DIR}" ]; then
        echo "! Warning: Base SEO skill not found in ~/.claude/skills/seo."
    fi

    echo ""
    echo "OpenSEO API key required."
    echo "Sign up or generate key at: https://app.openseo.so/settings/api-keys"
    echo ""

    read -r -s -p "OpenSEO API key (oseo_...): " API_KEY
    echo ""
    if [ -z "${API_KEY}" ]; then
        echo "x API key cannot be empty."
        exit 1
    fi

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR=""
    if [ -d "${SCRIPT_DIR}/skills/seo-openseo" ]; then
        SOURCE_DIR="${SCRIPT_DIR}/skills/seo-openseo"
    elif [ -f "${SCRIPT_DIR}/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}"
    fi

    if [ -n "${SOURCE_DIR}" ]; then
        mkdir -p "${SKILL_DIR}"
        cp -r "${SOURCE_DIR}/"* "${SKILL_DIR}/"
        echo "v Installed skill files to ${SKILL_DIR}"
    fi

    export CLAUDE_SEO_SECRET="${API_KEY}"
    python3 - "${MCP_CONFIG_FILE}" "${GEMINI_MCP_CONFIG}" <<'PYEOF'
import json, os, sys, tempfile

def update_file(filepath, key):
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as e:
            sys.exit(f"Error parsing {filepath}: {e}")
    mcp = data.setdefault('mcpServers', {})
    mcp['openseo'] = {
        'url': 'https://app.openseo.so/mcp',
        'headers': {
            'Authorization': f'Bearer {key}'
        }
    }
    dirname = os.path.dirname(filepath) or '.'
    os.makedirs(dirname, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dirname, prefix='.mcp_tmp.', suffix='.json')
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, filepath)
    print(f"v Configured OpenSEO MCP in {filepath}")

key = os.environ.get('CLAUDE_SEO_SECRET', '')
if not key:
    sys.exit("Missing secret")

update_file(sys.argv[1], key)
if len(sys.argv) > 2 and sys.argv[2] and os.path.exists(os.path.dirname(sys.argv[2])):
    update_file(sys.argv[2], key)
PYEOF
    unset CLAUDE_SEO_SECRET

    echo "Done! Try: /seo openseo keywords <query>"
}

main "$@"
