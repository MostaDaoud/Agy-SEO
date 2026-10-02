# OpenSEO Extension Uninstaller for Agy-SEO / Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "Uninstalling OpenSEO extension..." -ForegroundColor Yellow

$SkillDir = "$env:USERPROFILE\.claude\skills\seo-openseo"
$McpConfigFile = "$env:USERPROFILE\.claude.json"
$GeminiMcpConfigFile = "$env:USERPROFILE\.gemini\config\mcp_config.json"

if (Test-Path $SkillDir) {
    Remove-Item -Path $SkillDir -Recurse -Force
    Write-Host "v Removed $SkillDir" -ForegroundColor Green
}

$pyScript = @"
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
"@

$pyScript | python - $McpConfigFile $GeminiMcpConfigFile
Write-Host "Done. OpenSEO extension uninstalled." -ForegroundColor Green
