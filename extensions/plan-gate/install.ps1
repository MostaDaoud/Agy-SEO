# seo-plan-gate Extension Installer for Agy-SEO / Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  seo-plan-gate Extension - Installer" -ForegroundColor Cyan
Write-Host "  For Agy-SEO & Claude SEO" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$ClaudeDir = "$env:USERPROFILE\.claude"
$SkillDir = "$ClaudeDir\skills\seo-plan-gate"
$AgentsDir = "$ClaudeDir\agents"
$AgentFile = "$AgentsDir\seo-plan-gate-planner.md"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceSkill = "$ScriptDir\skills\seo-plan-gate"
$SourceAgent = "$ScriptDir\agents\seo-plan-gate-planner.md"

if (-not (Test-Path $SourceSkill)) {
    Write-Host "Error: Cannot find source skill directory at $SourceSkill" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $SourceAgent)) {
    Write-Host "Error: Cannot find source agent file at $SourceAgent" -ForegroundColor Red
    exit 1
}

# Ensure destination directories exist
if (-not (Test-Path $SkillDir)) {
    New-Item -ItemType Directory -Path $SkillDir -Force | Out-Null
}
if (-not (Test-Path $AgentsDir)) {
    New-Item -ItemType Directory -Path $AgentsDir -Force | Out-Null
}

# Copy skill files and agent
Copy-Item -Path "$SourceSkill\*" -Destination $SkillDir -Recurse -Force
Copy-Item -Path $SourceAgent -Destination $AgentFile -Force

Write-Host "Copied skill to $SkillDir" -ForegroundColor Green
Write-Host "Copied agent to $AgentFile" -ForegroundColor Green

# Verify enforcement using audit script
$AuditScript = "$ScriptDir\scripts\audit.py"
if (Test-Path $AuditScript) {
    Write-Host ""
    Write-Host "Verifying Lane A enforcement..." -ForegroundColor Yellow
    python $AuditScript $AgentFile
}

Write-Host ""
Write-Host "Done! seo-plan-gate is installed." -ForegroundColor Green
Write-Host "Note: Restart Claude Code to load new subagent definitions." -ForegroundColor Yellow
Write-Host "Try: /seo plan-gate <task>" -ForegroundColor Cyan
