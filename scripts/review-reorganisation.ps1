param(
    [string]$ProjectRoot = "."
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path $ProjectRoot).Path
Write-Host "This script is documentation-only for the prepared reorganised copy."
Write-Host "Use Git before applying structural changes to your working project:"
Write-Host "  git add ."
Write-Host "  git commit -m 'Backup before folder reorganisation'"
Write-Host "Prepared target structure: $root"
Write-Host "See PROJECT_STRUCTURE.md and compare against the reorganised ZIP."
