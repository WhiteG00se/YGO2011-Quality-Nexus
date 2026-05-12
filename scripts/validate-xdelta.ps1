param(
    [string]$SourceRom = "build\YGO2011-Nexus-Revival-0.5.nds",
    [string]$Patch = "Quality_Patch.xdelta",
    [string]$ExpectedRom = "build\YGO2011-Quality-Nexus.nds",
    [string]$VerifyOutputRom = "build\YGO2011-Quality-Nexus.from-patch.nds"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$xdelta = Join-Path $repoRoot "tools\bin\xdelta3.exe"

if (-not (Test-Path -LiteralPath $xdelta)) {
    throw "Missing xdelta3 CLI at tools\bin\xdelta3.exe."
}

if (-not (Test-Path -LiteralPath $Patch)) {
    throw "Missing xdelta patch: $Patch"
}

if (-not (Test-Path -LiteralPath $SourceRom)) {
    & (Join-Path $repoRoot "scripts\apply-revival-patch.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build $SourceRom."
    }
}

if (-not (Test-Path -LiteralPath $ExpectedRom)) {
    throw "Missing expected ROM for validation: $ExpectedRom. Run scripts\apply-quality-patch.py or scripts\create-xdelta-as-diff.ps1 first."
}

$outputDir = Split-Path -Parent $VerifyOutputRom
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

try {
    & $xdelta -d -f -s $SourceRom $Patch $VerifyOutputRom
    if ($LASTEXITCODE -ne 0) {
        throw "xdelta3 failed with exit code $LASTEXITCODE."
    }

    $expectedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ExpectedRom).Hash.ToUpperInvariant()
    $verifyHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $VerifyOutputRom).Hash.ToUpperInvariant()
    if ($expectedHash -ne $verifyHash) {
        throw "Patch validation failed. $ExpectedRom and $VerifyOutputRom do not match."
    }

    Write-Host "Validated $Patch against $ExpectedRom"
    Write-Host "Verified patch output SHA256: $expectedHash"
}
finally {
    if (Test-Path -LiteralPath $VerifyOutputRom) {
        Remove-Item -LiteralPath $VerifyOutputRom -Force
        Write-Host "Deleted temporary validation ROM $VerifyOutputRom"
    }
}
