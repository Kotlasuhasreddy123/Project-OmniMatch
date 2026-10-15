$ErrorActionPreference = 'Stop'
$base = 'http://localhost:8000'
$session = 'SMOKE-' + [guid]::NewGuid().ToString('N')
$start = Get-Date

$login = Invoke-RestMethod -Method Post -Uri "$base/api/v1/auth/login" -ContentType 'application/json' -Body '{"username":"clinical_staff","password":"Staff@12345"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$health = Invoke-RestMethod -Uri "$base/api/v1/health"
if (-not ($health.qdrant_connected -and $health.whisper_loaded)) { throw 'API dependencies are not ready.' }

$consentBody = @{ session_id = $session; action = 'CONSENT_GRANTED'; patient_pseudonym = 'DEMO-PATIENT' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/v1/consent" -Headers $headers -ContentType 'application/json' -Body $consentBody | Out-Null

$scriptedText = 'Doctor: What brings you in today? Patient: I have type 2 diabetes and take metformin. I also have high blood pressure. I do not have kidney disease. My mother had a stroke.'
$nlpBody = @{ transcription = $scriptedText; session_id = $session } | ConvertTo-Json
$nlp = Invoke-RestMethod -Method Post -Uri "$base/api/v1/nlp/extract" -Headers $headers -ContentType 'application/json' -Body $nlpBody
$approved = @($nlp.entities | Where-Object { -not $_.negated -and $_.context -eq 'patient' } | ForEach-Object { $_.status = 'approved'; $_ })
if ($approved.Count -lt 2) { throw 'Entity extraction returned fewer than two approvable patient findings.' }

$completeBody = @{ session_id = $session; approved_entities = $approved; evidence_spans = @() } | ConvertTo-Json -Depth 12
Invoke-RestMethod -Method Post -Uri "$base/api/v1/sessions/$session/complete" -Headers $headers -ContentType 'application/json' -Body $completeBody | Out-Null

$found = $null
for ($attempt = 1; $attempt -le 12; $attempt++) {
    $inbox = Invoke-RestMethod -Uri "$base/api/v1/inbox" -Headers $headers
    $found = @($inbox.items | Where-Object { $_.session_id -eq $session }) | Select-Object -First 1
    if ($found) { break }
    Start-Sleep -Seconds 5
}
if (-not $found) { throw 'No inbox item appeared within 60 seconds.' }
if ($found.matches.Count -lt 1) { throw 'The inbox item did not contain a trial match.' }
if (@($found.approved_entities | Where-Object { $_ -match 'kidney|stroke' }).Count -gt 0) {
    throw 'A negated or family-history condition leaked into approved matching terms.'
}

$elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
Write-Host "PASS: consent, extraction, human approval, async inbox and $($found.matches.Count) synthetic matches in $elapsed seconds." -ForegroundColor Green
Write-Host "Session: $session"
