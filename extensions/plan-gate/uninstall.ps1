# seo-plan-gate Extension Uninstaller for Agy-SEO / Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "Uninstalling seo-plan-gate extension..." -ForegroundColor Yellow

$ClaudeDir = "$env:USERPROFILE\.claude"
$SkillDir = "$ClaudeDir\skills\seo-plan-gate"
$AgentFile = "$ClaudeDir\agents\seo-plan-gate-planner.md"

if (Test-Path $SkillDir) {
    Remove-Item -Path $SkillDir -Recurse -Force
    Write-Host "Removed $SkillDir" -ForegroundColor Green
}

if (Test-Path $AgentFile) {
    Remove-Item -Path $AgentFile -Force
    Write-Host "Removed $AgentFile" -ForegroundColor Green
}

Write-Host "Done. seo-plan-gate extension uninstalled." -ForegroundColor Green
