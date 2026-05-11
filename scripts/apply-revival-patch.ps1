param(
    [string]$BaseRom = "YGO2011-Over_The_Nexus_USA_unpatched.nds",
    [string]$Patch = "YGO.Nexus.Revival.0.5.xdelta",
    [string]$Output = "build\YGO2011-Nexus-Revival-0.5.nds"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedBaseRomSha256 = "394A146733D118E0A685D5615213125D5A94FE72F05A3F9F988FA1418EFB5709"
$ExpectedPatchSha256 = "AB86C453B97BED34BFED2377570CEC16B674E63D01B1D67FAF19E6CBE075E182"
$ExpectedOutputSha256 = "80BBAB46CADB3194C907BF2290702956DA37936AB6BE5E6A001B35304C066F55"

function Assert-Sha256 {
    param(
        [string]$Path,
        [string]$Expected
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing file: $Path"
    }

    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
    if ($actual -ne $Expected) {
        throw "SHA256 mismatch for $Path. Expected $Expected but got $actual."
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$xdelta = Join-Path $repoRoot "tools\bin\xdelta3.exe"

if (-not (Test-Path -LiteralPath $xdelta)) {
    throw "Missing xdelta3 CLI at tools\bin\xdelta3.exe. Download it from https://github.com/jmacd/xdelta-gpl/releases/download/v3.0.11/xdelta3-3.0.11-x86_64.exe.zip"
}

Assert-Sha256 -Path $BaseRom -Expected $ExpectedBaseRomSha256
Assert-Sha256 -Path $Patch -Expected $ExpectedPatchSha256

$outputDir = Split-Path -Parent $Output
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

& $xdelta -d -f -s $BaseRom $Patch $Output
if ($LASTEXITCODE -ne 0) {
    throw "xdelta3 failed with exit code $LASTEXITCODE."
}

Assert-Sha256 -Path $Output -Expected $ExpectedOutputSha256
Write-Host "Wrote $Output"
