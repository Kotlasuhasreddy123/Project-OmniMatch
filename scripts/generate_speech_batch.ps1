# Offline fictional speech fixtures. Audio is returned in memory, never saved.
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $notes = @(
        'The patient has asthma and uses albuterol. The patient denies diabetes.',
        'The patient has type two diabetes and takes metformin. There is no kidney disease.',
        'Her mother had a stroke. The patient has high blood pressure and takes lisinopril.',
        'The patient reports migraine and nausea. No fever or chest pain is reported.',
        'The patient has rheumatoid arthritis and takes methotrexate.',
        'The patient has pneumonia and received amoxicillin. No history of tuberculosis.',
        'Possible endometriosis needs further review. The patient denies asthma.',
        'The patient has chronic pancreatitis. Her father had Parkinson disease.'
    )
    $rows = @()
    foreach ($note in $notes) {
        $buffer = New-Object System.IO.MemoryStream
        try {
            $voice.SetOutputToWaveStream($buffer)
            $voice.Speak($note)
            $rows += @{ reference = $note; audio_base64 = [Convert]::ToBase64String($buffer.ToArray()) }
        } finally { $buffer.Dispose() }
    }
    @{ voice = $voice.Voice.Name; cases = $rows } | ConvertTo-Json -Depth 5 -Compress
} finally { $voice.Dispose() }
