[CmdletBinding()]
param(
    [switch]$NoPause
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$exitCode = 0
Set-Location -LiteralPath $repoRoot

function Invoke-BuildStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "== $Name =="
    & $Action
}

function Write-FileSha256 {
    param(
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "MISSING  $Path"
        return
    }

    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
    Write-Host "$hash  $Path"
}

try {
    Invoke-BuildStep "Apply Nexus Revival patch" {
        & (Join-Path $repoRoot "scripts\apply-revival-patch.ps1")
        if ($LASTEXITCODE -ne 0) {
            throw "Nexus Revival build failed with exit code $LASTEXITCODE."
        }
    }

    Invoke-BuildStep "Build Quality ROM and xdelta patch" {
        & (Join-Path $repoRoot "scripts\create-xdelta-as-diff.ps1")
        if ($LASTEXITCODE -ne 0) {
            throw "Quality build failed with exit code $LASTEXITCODE."
        }
    }

    Invoke-BuildStep "Final SHA256 hashes" {
        Write-FileSha256 "YGO2011-Over_The_Nexus_USA_unpatched.nds"
        Write-FileSha256 "YGO.Nexus.Revival.0.5.xdelta"
        Write-FileSha256 "build\YGO2011-Nexus-Revival-0.5.nds"
        Write-FileSha256 "build\YGO2011-Quality-Nexus.nds"
        Write-FileSha256 "Quality_Patch.xdelta"
    }

    Write-Host ""
    Write-Host "Build completed successfully."
}
catch {
    Write-Host ""
    Write-Host "Build failed:"
    Write-Host $_.Exception.Message
    $exitCode = 1
}
finally {
    if (-not $NoPause) {
        Read-Host "Press Enter to close"
    }
}

exit $exitCode
