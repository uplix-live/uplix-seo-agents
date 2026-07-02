# Installation des agents SEO Uplix pour Claude Code (Windows)
# Usage : .\install.ps1            -> installe dans ~/.claude/skills (global)
#         .\install.ps1 -Project   -> installe dans .claude/skills du dossier courant
param([switch]$Project)

$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "skills"

if ($Project) {
    $dest = Join-Path (Get-Location) ".claude\skills"
} else {
    $dest = Join-Path $env:USERPROFILE ".claude\skills"
}

Write-Host "Installation des skills vers $dest ..."
New-Item -ItemType Directory -Force $dest | Out-Null
Get-ChildItem $src -Directory | ForEach-Object {
    Copy-Item $_.FullName -Destination (Join-Path $dest $_.Name) -Recurse -Force
    Write-Host "  + $($_.Name)"
}

Write-Host "`nInstallation des dependances Python ..."
python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
python -m playwright install chromium

Write-Host "`nTermine."
Write-Host "1. Copier .mcp.json.example -> .mcp.json a la racine de votre projet et renseigner vos cles."
Write-Host "2. Copier .env.example -> .env pour les scripts Python."
Write-Host "3. Relancer Claude Code puis tester : /agent-technique example.fr"
