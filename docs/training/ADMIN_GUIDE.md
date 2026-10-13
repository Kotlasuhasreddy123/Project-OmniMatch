# OmniMatch — Administrator Guide

**Audience:** IT admins, system operators, course instructors

---

## Initial Setup (15 minutes)

### Prerequisites
- Docker Desktop installed and running
- Git installed
- 8 GB RAM recommended (4 GB minimum)
- Ports 3000, 6333, 8000 free

### 1. Clone and Configure

```bash
git clone <your-repo-url> omni-match
cd omni-match
cp backend/.env.example backend/.env
```

Edit `backend/.env` — change at minimum:
```
JWT_SECRET_KEY=<random-32-char-string>
APP_SECRET_KEY=<different-random-32-char-string>
```

Generate random keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Start All Services

```bash
docker compose up --build
```

Wait for all health checks to pass (~2 minutes first run, ~30s after).

### 3. Seed Trial Data

```bash
# Inside running container
docker compose exec backend python scripts/seed_trials.py --max 50

# Or locally (with Python 3.10+ venv active)
cd backend && python scripts/seed_trials.py --conditions diabetes hypertension --max 100
```

### 4. Verify Installation

```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"ok","qdrant_connected":true,"whisper_loaded":true,...}
```

Open http://localhost:3000 → should show OmniMatch home page.

---

## Demo Users

| Username | Password | Role | Can Access |
|----------|----------|------|------------|
| `clinical_staff` | `Staff@12345` | CLINICAL_STAFF | All features except sync |
| `admin` | `Admin@12345` | ADMIN | All features including sync |

To add a real user, insert directly into SQLite:
```bash
docker compose exec backend python -c "
from passlib.context import CryptContext
import sqlite3, uuid
from datetime import datetime, timezone

pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')
conn = sqlite3.connect('omni_match.db')
conn.execute(
  'INSERT INTO users (id, username, hashed_pw, role, created_at) VALUES (?,?,?,?,?)',
  (str(uuid.uuid4()), 'newuser', pwd.hash('NewPass@123'), 'CLINICAL_STAFF', datetime.now(timezone.utc).isoformat())
)
conn.commit()
"
```

---

## Running Tests

### Backend Tests
```bash
# All tests
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# Or locally
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest tests/ -v --tb=short

# Specific test files
pytest tests/test_consent.py -v        # TEST-01
pytest tests/test_nlp_pipeline.py -v   # TEST-02
pytest tests/test_matching.py -v       # TEST-03, TEST-05
pytest tests/test_rbac.py -v           # TEST-08
pytest tests/test_exhaustive.py -v     # All 8 + performance
pytest tests/test_new_features.py -v   # 7 new features
```

### Frontend Tests
```bash
cd frontend
npm install --legacy-peer-deps
npm run test:run
```

### Security Scan
```bash
cd backend
pip install bandit
bandit -r app/ -c .bandit.yml -ll  # -ll = HIGH + MEDIUM severity only
```

---

## AWS Deployment

See `infrastructure/aws/cloudformation.yml` and `infrastructure/scripts/deploy_aws.sh`.

```bash
# Deploy to dev
chmod +x infrastructure/scripts/deploy_aws.sh
./infrastructure/scripts/deploy_aws.sh dev

# Tear down
./infrastructure/scripts/teardown_aws.sh dev
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### View Audit Logs (SQLite)
```bash
docker compose exec backend sqlite3 /app/data/omni_match.db \
  "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20;"
```

### View Application Logs
```bash
docker compose logs backend --tail=100 -f
docker compose logs frontend --tail=50
```

### Qdrant Dashboard
Open http://localhost:6333/dashboard → inspect `clinical_trials` collection.

### Embedding Cache Stats
```bash
curl http://localhost:8000/api/v1/health | python -m json.tool
```

---

## Seeding Options

```bash
# Default: all 15 conditions, 50 per condition
python scripts/seed_trials.py

# Specific conditions only
python scripts/seed_trials.py --conditions diabetes cancer --max 200

# Maximum coverage (takes 5-10 minutes)
python scripts/seed_trials.py --max 200
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Qdrant connection refused | Run `docker compose up qdrant` separately first |
| Whisper slow | Set `WHISPER_MODEL=tiny` in `.env` for demos |
| No trials in search results | Run `seed_trials.py` or admin sync API |
| JWT expired | Re-login; tokens expire after 8 hours |
| Port 8000 in use | `lsof -i :8000` then kill the process |
| `spacy` model missing | `python -m spacy download en_core_web_sm` |
| Docker out of memory | Set `WHISPER_MODEL=tiny` and restart |
