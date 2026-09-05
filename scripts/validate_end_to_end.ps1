param(
    [string]$ComposeFile = "infrastructure/docker/docker-compose.yml",
    [switch]$KeepContainers
)

$ErrorActionPreference = "Stop"
$exitCode = 1

$rootDir = Split-Path -Parent $PSScriptRoot
$composePath = Join-Path $rootDir $ComposeFile

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not available on PATH."
    exit 1
}

if (-not (Test-Path $composePath)) {
    Write-Error "Compose file not found: $composePath"
    exit 1
}

try {
    Write-Host ("$ docker compose -f {0} up --build --abort-on-container-exit --exit-code-from dbt" -f $composePath)
    docker compose -f $composePath up --build --abort-on-container-exit --exit-code-from dbt
    if ($LASTEXITCODE -ne 0) { throw "end-to-end validation failed with exit code $LASTEXITCODE" }

    $exitCode = 0
}
finally {
    if (-not $KeepContainers) {
        Write-Host ("$ docker compose -f {0} down" -f $composePath)
        docker compose -f $composePath down | Out-Host
    }
}

if ($exitCode -eq 0) {
    Write-Host 'End-to-end validation completed successfully.'
}

exit $exitCode
