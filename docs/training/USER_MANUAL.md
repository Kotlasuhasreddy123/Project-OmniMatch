# OmniMatch — Clinical Staff User Manual

**Version:** 1.0 | **Course:** CPSC-69100 Fall 2026 | **Team:** HealthTech Innovation Labs

---

## Overview

OmniMatch is an ambient AI system that listens to doctor-patient conversations,
extracts clinical information, and matches patients to relevant clinical trials —
all without interrupting your workflow. Trial matches arrive in your inbox for
review at a convenient time, never as pop-up alerts during patient visits.

**Important:** All patient data in this system is synthetic/simulated. No real
patient health information (PHI) is processed.

---

## Quick Reference Card

```
1. Sign in at http://localhost:3000/login
   Username: clinical_staff | Password: Staff@12345

2. Start Session → /session
   ↓ Toggle Patient Consent ON (required before recording)
   ↓ Click microphone to record ambient audio
   ↓ Click stop when visit ends

3. Verify Entities → /verify (auto-redirect)
   ↓ Review AI-extracted terms
   ↓ Click APPROVE on correct terms
   ↓ Click REJECT on incorrect terms
   ↓ Click "Submit Verified Entities"

4. Check Inbox → /inbox (within 60 seconds)
   ↓ Review matched trials
   ↓ View per-criterion eligibility breakdown
   ↓ Check Missing Variables checklist
   ↓ Click "Initiate Referral" if appropriate
```

---

## Step-by-Step Guide

### Step 1: Sign In

1. Open your browser and navigate to **http://localhost:3000**
2. Click **Sign In** in the navigation bar
3. Enter your credentials:
   - Username: `clinical_staff`
   - Password: `Staff@12345`
4. Click **Sign In** — you will be redirected to the home page

> **Security:** Your session token expires after 8 hours. You will be
> automatically redirected to the login page when it expires.

---

### Step 2: Start a Visit Session

Navigate to **New Session** (`/session`).

#### 2a. Patient Consent Toggle (MANDATORY — REQ-01)

The **Patient Consent toggle** is a legal and technical requirement.
The microphone **cannot activate** until consent is enabled.

1. Read the consent description to the patient
2. With the patient's verbal agreement, click the **Patient Consent** toggle
3. The status indicator changes from red "Consent required" to green "Consent active"
4. An audit log entry is automatically created with timestamp

> **⚠️ Important:** If the patient declines consent, do NOT enable the toggle.
> The system will not allow recording without consent.

#### 2b. Audio Recording

Once consent is active:

1. Click the **microphone button** (blue circle)
2. The button turns red and pulses — recording is active
3. Conduct your normal patient visit — speak naturally
4. Click the **stop button** (red square) when finished

**What OmniMatch listens for:**
- Current medical conditions ("Patient has diabetes...")
- Current medications ("She is on metformin...")
- Symptoms ("He reports chest pain...")
- Things NOT present ("No history of hypertension...")
- Family history ("Mother had breast cancer...")

**What OmniMatch ignores:**
- Negated conditions ("denies..." / "no history of...")
- Family history (tagged separately, not used for patient matching)
- Hypothetical statements ("if the patient develops...")

#### 2c. Transcript Review (NEW — Feature 6)

After recording stops, the transcription appears with a **confidence heatmap**:

- **Green** words: High confidence (>70%) — correct
- **Amber** words: Low confidence (50-70%) — review recommended
- **Red** words: Very low confidence (<50%) — likely incorrect

If you see amber or red words near clinical terms:
1. Click **Edit** on the transcript panel
2. Correct the highlighted words
3. Click **Save Correction**

Your correction is flagged as human-verified in the audit log.

---

### Step 3: Verify Extracted Entities

After processing, you are automatically redirected to the **Verification screen** (`/verify`).

The AI has extracted clinical terms from the transcript. **You must review each one.**

#### Understanding Entity Cards

Each extracted term appears as a card showing:
- **Term**: The clinical entity (e.g., "type 2 diabetes")
- **Type**: DISEASE / SYMPTOM / MEDICATION / PROCEDURE / LAB_VALUE
- **Confidence**: How certain the AI is (shown as %)
- **Context badges**:
  - `Negated` — detected as NOT present ("denies diabetes") — automatically excluded
  - `Family History` — detected as family context — automatically excluded
  - `Hypothetical` — conditional/uncertain — automatically excluded

#### Your Decision

For each patient-context entity card:

| Button | When to use |
|--------|-------------|
| **✓ Approve** | The term is accurate and represents a current patient condition |
| **✗ Reject** | The term is incorrect, outdated, or not relevant to trial eligibility |

> **Rule:** Only APPROVED, non-negated, patient-context entities are sent to
> the trial matching engine. Rejected terms are **never** used.

#### Submit

Once you have reviewed all entities:
1. At least **one entity must be approved**
2. Click **"Submit X Approved Entities for Matching"**
3. The system begins asynchronous trial matching in the background

---

### Step 4: Review the Clinical Trial Inbox

Navigate to **Inbox** (`/inbox`). Trial matches appear within **60 seconds** of submission.

#### Inbox Item Overview

Each inbox item shows:
- **Session ID** and timestamp
- Number of trials matched
- Approved entity terms used

Click any item to expand it.

#### Trial Match Details

Each matched trial shows:

**1. Enrollment Readiness Score (NEW)**
A 0–100% composite score:
- ≥70% (green): Strong match — worth pursuing
- 45-69% (amber): Partial match — review carefully
- <45% (red): Weak match — significant eligibility gaps

**2. Per-Criterion Eligibility Breakdown (NEW)**
Each eligibility criterion is individually evaluated:
- ✅ **Met** — Patient condition found in approved entities
- ❌ **Not Met** — Patient explicitly does NOT have this condition
- ⚠️ **Missing** — Not mentioned in the visit; follow-up needed
- ❓ **Unknown** — Requires a lab value not discussed (HbA1c, eGFR, etc.)

**3. Missing Variables Checklist**
Items that were not found in the transcript that the trial requires.
These are items to discuss with the patient or retrieve from EHR.

**4. Geographic Proximity (NEW)**
Shows the distance to the nearest trial site from your clinic.
Trials within 200 miles are ranked higher.

#### Initiating a Referral (NEW — Feature 5)

If a trial looks appropriate:
1. Click **"Initiate Referral"** on the trial card
2. The system logs the referral with your username and timestamp
3. If a webhook is configured, a notification is sent automatically

#### Mark as Reviewed

When you've finished reviewing an inbox item:
1. Click **"Mark as Reviewed"**
2. The item moves from "New" to "Reviewed" status

---

### Step 5: Patient Timeline (NEW — Feature 3)

Navigate to **Timeline** (`/timeline`).

Enter a patient pseudonym to see their entity history across **all** visit sessions.
Entities that appear in multiple sessions are marked with a multiplier (×2, ×3, etc.).

**Why this matters:** A patient who mentions diabetes in visit 1 and reports
HbA1c 8.2 in visit 3 now meets eligibility criteria for a trial that required
both. The timeline detects this "eligibility unlock" automatically.

---

## Frequently Asked Questions

**Q: What if the patient revokes consent mid-session?**
A: Click the Patient Consent toggle to OFF immediately. Recording stops,
the audio buffer is cleared from memory, and a CONSENT_REVOKED audit entry is logged.

**Q: Can I approve a negated entity?**
A: Negated entities ("denies diabetes") and family history entities are automatically
excluded from matching even if you approve them. The backend enforces this as a safety rule.

**Q: How long do inbox items stay?**
A: Items remain until you mark them as reviewed. There is no automatic expiry in this version.

**Q: What if no trials are found?**
A: This can happen if: (a) Qdrant hasn't been seeded with trial data yet (ask your admin
to run the trial sync), or (b) the approved entities don't match any currently recruiting trials.

**Q: Is this system connected to the real EHR?**
A: No. OmniMatch is a standalone prototype for academic demonstration. There is no
EHR write-back. All patient data in demos is synthetic.

**Q: What does "Unknown" mean in the eligibility breakdown?**
A: It means the trial requires a specific lab value (HbA1c, eGFR, blood pressure
reading, etc.) that was not spoken during the visit. You would need to check the EHR
or ask the patient for that information.

---

## Keyboard Shortcuts (Accessibility)

| Key | Action |
|-----|--------|
| `Tab` | Move between interactive elements |
| `Space` / `Enter` | Activate button or toggle |
| `Esc` | Close expanded panels |
| `Shift+Tab` | Move backwards |

All elements meet **WCAG 2.1 Level AA** accessibility standards.
Screen reader users: all buttons have descriptive aria-labels.
