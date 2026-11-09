"""RAM-only synthetic TTS ASR development benchmark, never clinical validation."""
import argparse
import base64
import io
import json
import re
import sys
import time
import wave
from app.transcription.whisper_service import TranscriptionService


def words(text):
    # Lowercase/punctuation normalization only; substitutions are not forgiven
    # through hand-written medical spelling or number replacement rules.
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def edits(reference, prediction):
    previous = list(range(len(prediction)+1))
    for i, token in enumerate(reference, 1):
        row = [i]
        for j, other in enumerate(prediction, 1):
            row.append(min(row[-1]+1, previous[j]+1, previous[j-1]+(token != other)))
        previous = row
    return previous[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['base', 'small'], required=True)
    options = parser.parse_args()
    batch = json.load(sys.stdin)
    import torch
    torch.set_num_threads(4)
    service = TranscriptionService(options.model)
    results = []
    for row in batch['cases']:
        audio = base64.b64decode(row['audio_base64'], validate=True)
        with wave.open(io.BytesIO(audio)) as wav:
            seconds = wav.getnframes()/wav.getframerate()
        start = time.perf_counter()
        result = service.transcribe_buffer(io.BytesIO(audio))
        expected, actual = words(row['reference']), words(result['transcription'])
        results.append(dict(reference=row['reference'], transcription=result['transcription'],
                            reference_words=len(expected), errors=edits(expected, actual),
                            audio_seconds=round(seconds, 3), processing_seconds=round(time.perf_counter()-start, 3)))
    total, errors = sum(row['reference_words'] for row in results), sum(row['errors'] for row in results)
    report = dict(model=options.model, voice=batch['voice'], cases=results, reference_words=total,
                  errors=errors, word_error_rate=errors/total,
                  provenance='Eight author-created fictional notes spoken by one offline Windows TTS voice. Audio was passed in memory only.',
                  limits='Synthetic single-speaker development check. Not doctor/patient accents, ambient noise, clinical speech validation or model fine-tuning.')
    print('SPEECH_REPORT_JSON='+json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
