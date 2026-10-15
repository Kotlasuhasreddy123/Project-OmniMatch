param([switch]$SkipBuild)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop is required. Install and start Docker Desktop, then run this script again.'
}
docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'Docker Desktop is not ready. Open Docker Desktop and wait until the engine is running.'
}

if ($SkipBuild) {
    docker compose up -d
} else {
    docker compose up -d --build
}
if ($LASTEXITCODE -ne 0) { throw 'The OmniMatch containers did not start.' }

Write-Host 'Waiting for the API, trial index, and speech model. The first run may download free models.'
$ready = $false
for ($attempt = 1; $attempt -le 120; $attempt++) {
    Start-Sleep -Seconds 5
    try {
        $health = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' -TimeoutSec 5
        $trialState = Invoke-RestMethod -Uri 'http://localhost:6333/collections/clinical_trials_demo' -TimeoutSec 5
        if ($health.qdrant_connected -and $health.whisper_loaded -and $trialState.result.points_count -ge 3) {
            $ready = $true
            break
        }
    } catch { }
}

if (-not $ready) {
    docker compose ps
    docker compose logs --tail=80 backend
    throw 'Preflight did not pass. Do not use the live demo until the errors above are resolved.'
}

Write-Host 'OmniMatch is ready: microphone transcription, Qdrant, and three synthetic trials.' -ForegroundColor Green
Write-Host 'Open http://localhost:3000 and sign in as clinical_staff / Staff@12345.'
Start-Process 'http://localhost:3000'
