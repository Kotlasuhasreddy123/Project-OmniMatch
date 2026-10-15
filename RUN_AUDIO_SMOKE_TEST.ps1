$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech

$base = 'http://localhost:8000'
$session = 'AUDIO-' + [guid]::NewGuid().ToString('N')
$login = Invoke-RestMethod -Method Post -Uri "$base/api/v1/auth/login" -ContentType 'application/json' -Body '{"username":"clinical_staff","password":"Staff@12345"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$consentBody = @{ session_id = $session; action = 'CONSENT_GRANTED'; patient_pseudonym = 'SYNTHETIC' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/v1/consent" -Headers $headers -ContentType 'application/json' -Body $consentBody | Out-Null

$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$stream = New-Object System.IO.MemoryStream
try {
    $speech.SetOutputToWaveStream($stream)
    $speech.Speak('I have type two diabetes. I take metformin. I do not have kidney disease.')
    $bytes = $stream.ToArray()
    if ($bytes.Length -lt 1000) { throw 'Synthetic speech generation failed.' }
    $result = Invoke-RestMethod -Method Post -Uri "$base/api/v1/audio/transcribe?session_id=$session" -Headers $headers -ContentType 'audio/wav' -Body $bytes -TimeoutSec 180
    if (-not $result.transcription.Trim()) { throw 'Whisper returned an empty transcript.' }
    Write-Host "PASS: in-memory synthetic speech produced a transcript in $($result.duration_seconds) seconds." -ForegroundColor Green
    Write-Host "Transcript: $($result.transcription)"
} finally {
    $speech.Dispose()
    $stream.Dispose()
}
