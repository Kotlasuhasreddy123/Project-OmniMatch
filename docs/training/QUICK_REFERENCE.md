# OmniMatch — 1-Page Quick Reference Card

## Sign In
URL: `http://localhost:3000/login`
| User | Password | Role |
|------|----------|------|
| `clinical_staff` | `Staff@12345` | Clinical Staff |
| `admin` | `Admin@12345` | Admin |

---

## Workflow (5 steps, ~3 minutes)

```
① /session  → Toggle CONSENT ON → Record audio → Stop recording
② /verify   → APPROVE correct entities → REJECT incorrect → Submit
③ /inbox    → Results appear in <60 seconds → Review trials
④ /inbox    → Click trial → View eligibility breakdown → Check missing variables
⑤ /inbox    → Click "Initiate Referral" → Mark as Reviewed
```

---

## Entity Chip Decisions

| See this | Do this |
|----------|---------|
| Correct condition ("diabetes") | ✓ **APPROVE** |
| Wrong/outdated term | ✗ **REJECT** |
| Badge: `Negated` | Auto-excluded (no action needed) |
| Badge: `Family History` | Auto-excluded (no action needed) |

---

## Enrollment Readiness Score

| Score | Color | Meaning |
|-------|-------|---------|
| ≥70% | 🟢 Green | Strong match — pursue |
| 45-69% | 🟡 Amber | Partial — check criteria |
| <45% | 🔴 Red | Weak — significant gaps |

---

## Criterion Verdicts

| Icon | Label | Meaning |
|------|-------|---------|
| ✅ | Met | Patient has this condition (confirmed) |
| ❌ | Not Met | Patient explicitly does NOT have this |
| ⚠️ | Missing | Not mentioned in visit — follow up |
| ❓ | Unknown | Lab value needed (HbA1c, eGFR, etc.) |

---

## Keyboard Shortcuts

`Tab` navigate · `Space/Enter` activate · `Esc` close · `Shift+Tab` back

---

## If Something Goes Wrong

| Problem | Solution |
|---------|---------|
| Microphone won't start | Check consent toggle is ON |
| No entities found | Re-record or type transcript manually |
| Inbox empty after 2 min | Ask admin to seed trial database |
| Login fails | Check username/password, try admin |
| Transcript errors | Use Edit button on transcript heatmap |
