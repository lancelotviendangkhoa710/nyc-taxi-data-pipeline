param(
    [string]$ComposeFile = "infrastructure/docker/docker-compose.local.yml",
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
    Write-Host ("$ docker compose -f {0} up -d postgres" -f $composePath)
    docker compose -f $composePath up -d postgres
    if ($LASTEXITCODE -ne 0) { throw "postgres startup failed with exit code $LASTEXITCODE" }

    Write-Host ("$ docker compose -f {0} exec -T postgres pg_isready -U postgres" -f $composePath)
    docker compose -f $composePath exec -T postgres pg_isready -U postgres
    if ($LASTEXITCODE -ne 0) { throw "postgres readiness check failed with exit code $LASTEXITCODE" }

    Write-Host ("$ docker compose -f {0} run --rm spark-etl" -f $composePath)
    docker compose -f $composePath run --rm spark-etl
    if ($LASTEXITCODE -ne 0) { throw "spark-etl failed with exit code $LASTEXITCODE" }

    Write-Host ("$ docker compose -f {0} run --rm --no-deps dbt" -f $composePath)
    docker compose -f $composePath run --rm --no-deps dbt
    if ($LASTEXITCODE -ne 0) { throw "dbt failed with exit code $LASTEXITCODE" }

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
