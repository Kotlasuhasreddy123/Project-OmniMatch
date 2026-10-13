#!/bin/bash
# OmniMatch — Complete cURL API Reference
# Every endpoint with expected responses.
# Usage: source curl_examples.sh or run individual commands.

BASE="http://localhost:8000"

echo "════════════════════════════════════════════════"
echo "  OmniMatch API — Complete cURL Reference"
echo "════════════════════════════════════════════════"

# ── 0. Health check (public) ─────────────────────────────────────────────
echo -e "\n[0] Health Check"
curl -s "$BASE/api/v1/health" | python -m json.tool

# ── 1. Authentication ─────────────────────────────────────────────────────
echo -e "\n[1] Login — Clinical Staff"
TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"clinical_staff","password":"Staff@12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:40}..."

echo -e "\n[1b] Login — Admin"
ADMIN_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo -e "\n[1c] Login — Wrong password (expect 401)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"clinical_staff","password":"wrongpassword"}'

# ── 2. Consent (REQ-01) ───────────────────────────────────────────────────
SESSION_ID="demo-session-$(date +%s)"
echo -e "\n[2] Log Consent GRANTED"
curl -s -X POST "$BASE/api/v1/consent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"session_id\":\"$SESSION_ID\",\"action\":\"CONSENT_GRANTED\",\"patient_pseudonym\":\"REDACTED\"}" \
  | python -m json.tool

echo -e "\n[2b] Consent — No auth (expect 401)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/api/v1/consent" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"s1","action":"CONSENT_GRANTED"}'

# ── 3. NLP Extraction (REQ-03) ────────────────────────────────────────────
echo -e "\n[3] Extract Clinical Entities"
curl -s -X POST "$BASE/api/v1/nlp/extract" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"transcription\": \"The patient has type 2 diabetes and hypertension. She denies chest pain. Family history of stroke in father. On metformin and lisinopril.\",
    \"session_id\": \"$SESSION_ID\"
  }" | python -m json.tool

echo -e "\n[3b] Extract — Long-distance negation"
curl -s -X POST "$BASE/api/v1/nlp/extract" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"transcription\": \"Imaging did not reveal any evidence of malignancy. Rules out COPD at this time. Patient confirmed with asthma.\",
    \"session_id\": \"$SESSION_ID\"
  }" | python -m json.tool

# ── 4. Audio Transcription (REQ-02, REQ-08) ───────────────────────────────
echo -e "\n[4] Transcribe Audio (WAV file — requires real audio)"
# Generate a 1-second silent WAV for testing
python3 -c "
import wave, io, struct
buf = io.BytesIO()
with wave.open(buf, 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
    f.writeframes(b'\x00\x00' * 16000)
with open('/tmp/test_silence.wav', 'wb') as f:
    f.write(buf.getvalue())
print('Silent WAV created: /tmp/test_silence.wav')
"
curl -s -X POST "$BASE/api/v1/audio/transcribe" \
  -H "Authorization: Bearer $TOKEN" \
  -F "session_id=$SESSION_ID" \
  -F "audio_file=@/tmp/test_silence.wav;type=audio/wav" \
  | python -m json.tool

echo -e "\n[4b] Transcribe — Wrong MIME (expect 415)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/api/v1/audio/transcribe" \
  -H "Authorization: Bearer $TOKEN" \
  -F "session_id=s1" \
  -F "audio_file=@/etc/hostname;type=text/plain"

# ── 5. Trial Matching (REQ-05, REQ-06) ────────────────────────────────────
echo -e "\n[5] Search Trials (with proximity ranking, clinic ZIP=10001)"
curl -s -X POST "$BASE/api/v1/match/search?clinic_zip=10001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"approved_entities\": [
      {\"term\":\"type 2 diabetes\",\"entity_type\":\"DISEASE\",\"negated\":false,
       \"context\":\"patient\",\"confidence\":0.92,\"status\":\"approved\"},
      {\"term\":\"hypertension\",\"entity_type\":\"DISEASE\",\"negated\":false,
       \"context\":\"patient\",\"confidence\":0.88,\"status\":\"approved\"}
    ],
    \"session_id\": \"$SESSION_ID\"
  }" | python -m json.tool

echo -e "\n[5b] Search — All rejected (expect 400, TEST-03)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/api/v1/match/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"approved_entities\": [
      {\"term\":\"diabetes\",\"entity_type\":\"DISEASE\",\"negated\":false,
       \"context\":\"patient\",\"confidence\":0.9,\"status\":\"rejected\"}
    ],
    \"session_id\": \"s-rej\"
  }"

# ── 6. Session completion (REQ-07) ────────────────────────────────────────
echo -e "\n[6] Complete Session (triggers async inbox population)"
curl -s -X POST "$BASE/api/v1/sessions/$SESSION_ID/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"approved_entities\": [
      {\"term\":\"type 2 diabetes\",\"entity_type\":\"DISEASE\",\"negated\":false,
       \"context\":\"patient\",\"confidence\":0.92,\"status\":\"approved\"}
    ]
  }" | python -m json.tool

# ── 7. Inbox (REQ-07, REQ-10) ─────────────────────────────────────────────
echo -e "\n[7] Waiting 5s for inbox population..."
sleep 5

echo -e "\n[7] List Inbox"
INBOX=$(curl -s "$BASE/api/v1/inbox" -H "Authorization: Bearer $TOKEN")
echo "$INBOX" | python -m json.tool
ITEM_ID=$(echo "$INBOX" | python -c "import sys,json; items=json.load(sys.stdin)['items']; print(items[0]['id'] if items else '')" 2>/dev/null)

if [ -n "$ITEM_ID" ]; then
  echo -e "\n[7b] Get Inbox Item: $ITEM_ID"
  curl -s "$BASE/api/v1/inbox/$ITEM_ID" -H "Authorization: Bearer $TOKEN" | python -m json.tool

  echo -e "\n[7c] Mark Reviewed"
  curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE \
    "$BASE/api/v1/inbox/$ITEM_ID" -H "Authorization: Bearer $TOKEN"
fi

echo -e "\n[7d] Inbox — No auth (expect 401, TEST-08)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$BASE/api/v1/inbox"

# ── 8. Patient Timeline (Feature 3) ───────────────────────────────────────
echo -e "\n[8] Get Patient Timeline"
curl -s "$BASE/api/v1/timeline/REDACTED" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# ── 9. Referral (Feature 5) ───────────────────────────────────────────────
echo -e "\n[9] Initiate Referral"
curl -s -X POST "$BASE/api/v1/referrals" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"inbox_item_id\": \"${ITEM_ID:-placeholder}\",
    \"nct_id\": \"NCT04442451\",
    \"session_id\": \"$SESSION_ID\",
    \"trial_title\": \"Mechanisms of Fatigability With Diabetes\",
    \"met_criteria\": [\"Patients with type 2 diabetes\"],
    \"patient_pseudo\": \"REDACTED\"
  }" | python -m json.tool

# ── 10. Trials Sync (Admin, TEST-04) ──────────────────────────────────────
echo -e "\n[10] Trigger Trial Sync (Admin token)"
curl -s -X POST "$BASE/api/v1/trials/sync" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo -e "\n[10b] Sync — Clinical Staff (expect 403)"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "$BASE/api/v1/trials/sync" \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n\n════ All tests complete ════"
