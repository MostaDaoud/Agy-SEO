# OpenSEO Extension Installer for Agy-SEO / Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  OpenSEO Extension - Installer" -ForegroundColor Cyan
Write-Host "  For Agy-SEO & Claude SEO" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$SkillDir = "$env:USERPROFILE\.claude\skills\seo-openseo"
$SeoSkillDir = "$env:USERPROFILE\.claude\skills\seo"
$McpConfigFile = "$env:USERPROFILE\.claude.json"
$GeminiMcpConfigFile = "$env:USERPROFILE\.gemini\config\mcp_config.json"

# Check prerequisites
if (-not (Test-Path $SeoSkillDir)) {
    Write-Host "x Claude SEO is not installed in ~/.claude/skills/seo." -ForegroundColor Yellow
} else {
    Write-Host "v Claude SEO detected" -ForegroundColor Green
}

# Prompt for API key
Write-Host ""
Write-Host "OpenSEO API key required." -ForegroundColor Yellow
Write-Host "Sign up or generate key at: https://app.openseo.so/settings/api-keys"
Write-Host ""

$apiKey = Read-Host "OpenSEO API key (oseo_...)" -AsSecureString
$apiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
if ([string]::IsNullOrWhiteSpace($apiKeyPlain)) {
    Write-Host "x API key cannot be empty." -ForegroundColor Red
    exit 1
}

# Determine source directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = $null
if (Test-Path "$ScriptDir\skills\seo-openseo\SKILL.md") {
    $SourceDir = "$ScriptDir\skills\seo-openseo"
} elseif (Test-Path "$ScriptDir\SKILL.md") {
    $SourceDir = $ScriptDir
} else {
    $RootAgy = Split-Path -Parent (Split-Path -Parent $ScriptDir)
    if (Test-Path "$RootAgy\skills\seo-openseo\SKILL.md") {
        $SourceDir = "$RootAgy\skills\seo-openseo"
    }
}

if ($null -ne $SourceDir) {
    if (-not (Test-Path $SkillDir)) {
        New-Item -ItemType Directory -Path $SkillDir -Force | Out-Null
    }
    Copy-Item -Path "$SourceDir\*" -Destination $SkillDir -Recurse -Force
    Write-Host "v Copied skill files to $SkillDir" -ForegroundColor Green
}

# Python script for atomic JSON merge
$pyScript = @"
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

claude_json = sys.argv[1]
update_file(claude_json, key)

if len(sys.argv) > 2 and sys.argv[2]:
    gemini_json = sys.argv[2]
    if os.path.exists(os.path.dirname(gemini_json)):
        update_file(gemini_json, key)
"@

$env:CLAUDE_SEO_SECRET = $apiKeyPlain
try {
    $pyScript | python - $McpConfigFile $GeminiMcpConfigFile
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update MCP configuration."
    }
} finally {
    Remove-Item Env:CLAUDE_SEO_SECRET -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Done! OpenSEO MCP is configured." -ForegroundColor Green
Write-Host "Try: /seo openseo keywords <query>" -ForegroundColor Cyan
