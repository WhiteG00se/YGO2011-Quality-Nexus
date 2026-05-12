param(
    [string]$SourceRom = "build\YGO2011-Nexus-Revival-0.5.nds",
    [string]$OutputRom = "build\YGO2011-Quality-Nexus.nds",
    [string]$Patch = "Quality_Patch.xdelta"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$xdelta = Join-Path $repoRoot "tools\bin\xdelta3.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing Python virtual environment at .venv\Scripts\python.exe. Install requirements from requirements.txt first."
}

if (-not (Test-Path -LiteralPath $xdelta)) {
    throw "Missing xdelta3 CLI at tools\bin\xdelta3.exe."
}

if (-not (Test-Path -LiteralPath $SourceRom)) {
    & (Join-Path $repoRoot "scripts\apply-revival-patch.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build $SourceRom."
    }
}

& $python (Join-Path $repoRoot "scripts\apply-quality-patch.py")
if ($LASTEXITCODE -ne 0) {
    throw "Quality ROM build failed with exit code $LASTEXITCODE."
}

& $xdelta -e -f -s $SourceRom $OutputRom $Patch
if ($LASTEXITCODE -ne 0) {
    throw "xdelta3 encode failed with exit code $LASTEXITCODE."
}

& (Join-Path $repoRoot "scripts\validate-xdelta.ps1") -SourceRom $SourceRom -Patch $Patch -ExpectedRom $OutputRom
if ($LASTEXITCODE -ne 0) {
    throw "xdelta validation failed with exit code $LASTEXITCODE."
}

Write-Host "Wrote $OutputRom"
Write-Host "Wrote $Patch"
