# Automatic credential-request emails

This optional Google Apps Script checks your WorkOS waitlist every five minutes and sends one professional-details request to each new pending applicant. Replies go directly to **suhasreddykotla222@gmail.com**. You review the evidence and approve access manually in WorkOS.

It runs on Google's service while your laptop is off. It does not need a public Python backend, a paid email provider, or a public webhook. It does not grant access or change WorkOS records.

## Current status

The script and email template are implemented. Twelve local automated tests passed using mocked Google and WorkOS services. On November 17, 2026, the owner deployment successfully initialized against WorkOS, sent a test message to the owner that was confirmed in Gmail, and completed the enable function. No applicant signup-to-delivery test has been completed yet. New installations are disabled by default and must complete the setup and authorization below; source files alone do not enable sending.

## One-time setup

1. Sign in to [Google Apps Script](https://script.google.com/home/start) using **suhasreddykotla222@gmail.com**. Create a new project named **OmniMatch credential requests**.
2. Replace the contents of `Code.gs` with the included [Code.gs](Code.gs). Save it.
3. Open **Project Settings** and enable **Show appsscript.json manifest file in editor**. Replace the manifest with the included [appsscript.json](appsscript.json). Save it.
4. In **Project Settings → Script Properties**, add:

| Property | Value |
| --- | --- |
| `WORKOS_API_KEY` | Your private server API key for the same WorkOS environment used by OmniMatch |
| `OWNER_EMAIL` | `suhasreddykotla222@gmail.com` |
| `PORTAL_URL` | `https://omnimatch-research.onrender.com/login/` |
| `WORKOS_WAITLIST_ID` | Optional if that environment has exactly one waitlist; otherwise enter the intended waitlist ID |
| `SEND_ENABLED` | `false` |

**Enter the API key directly in Script Properties. Never paste it into chat, source code, a screenshot, or GitHub.** Keep the project private: project editors can access Script Properties. Use the narrowest available WorkOS key permissions. The code makes only read requests to WorkOS, but that does not itself limit the underlying key's permissions.

5. Select and run **initializeAutomation**. Google will ask you to authorize sending mail, external requests, your account email, and script triggers. Check that the account shown is yours. Complete authorization yourself; do not bypass any Google security warning. This function validates the settings and sets a start date. It sends nothing.
6. Run **sendTestToOwner**. One test email goes only to your owner address. Read it and confirm the wording and reply address. Do not use a real physician's identity for a test account.
7. Run **previewNewRequests**. This sends nothing and reports only counts. Existing waitlist entries from before initialization are deliberately excluded, so they will not receive an unexpected batch email.
8. Run **enableAutomation**. This installs one five-minute trigger and enables sending. No further manual action is needed for new applicants while the trigger, credentials and quotas remain valid.
9. Submit a new request using an email address you control. Within roughly five minutes, confirm that exactly one email arrives. Run **pollWaitlist** again and confirm that there is no duplicate. Reply with synthetic test details and confirm the reply arrives in your owner inbox.

Automatic trigger timing is approximate, not an instant-delivery guarantee. The user may also receive WorkOS's own waitlist-confirmation email; the credential request is a separate message.

## What the applicant receives

The email asks for name, designation/specialty, institution, country of practice, license or registration number, issuing authority, and an official registry or staff-directory link. A phone number with country code is optional. It requests no patient information, passwords, email codes, government ID documents or unredacted ID-card photos. Replies are for manual review, not model training.

## How you approve access

1. Review the reply and compare the details with the official licensing authority or institution. A matching NPI alone does not verify the applicant's identity or current licensure.
2. In WorkOS, review and approve the intended entry under **Users → Waitlist**.
3. Under **Organizations → OmniMatch Academic Team → Users**, confirm active membership and assign **OmniMatch Clinical Staff**. Keep the owner role restricted to the owner.
4. The signed-in applicant's pending page checks their permissions every 15 seconds while visible. When the role is ready, it opens their workspace. Their visits stay private to their account.

This script never approves an applicant, changes a role, reads credential replies, opens attachments, or judges professional eligibility. Review replies yourself. Store only evidence needed for review, restrict mailbox access and delete verification correspondence when no longer needed. No automated retention policy is installed in Gmail.

## Pause and recover

- Run **pauseAutomation**, or set `SEND_ENABLED=false`, to stop sending. The timer may continue running harmlessly. You can remove only the `pollWaitlist` trigger from the Triggers page to stop scheduled executions entirely.
- Do not delete `DELIVERY_...` properties casually. They prevent duplicate emails.
- A `sent` marker means the Google send call returned successfully; it does not prove delivery or that the recipient read it.
- A `needs_review` marker means the send outcome is uncertain, including a crash during delivery. Check Gmail Sent mail before deciding whether to contact that person manually. The script will not retry an ambiguous send automatically.
- Zero remaining mail quota defers new messages to a later run. Authentication, malformed records and pagination-limit failures stop the batch instead of emailing unchecked addresses.
- The small-project limit is 500 pending entries and at most 10 messages per run. Monitor Apps Script's Executions page and storage usage as the waitlist grows. This is not a bulk-mail service.
- Changing WorkOS environments requires rechecking both the API key and waitlist ID. Removing the API key or revoking Google authorization stops successful runs.

## Cost and verification

No paid service is required by this implementation. Existing account limits still apply. Google's documented consumer Apps Script limit is currently 100 email recipients per day, shared with applicable script email use; quotas can change. The script checks the remaining quota before sending. Do not enable billing or paid services for this workflow.

Run the local tests from the repository root:

```powershell
node --test scripts/credential-email/automation.test.cjs
```

The tests cover once-only sends, disabled mode, old requests, quota exhaustion, invalid addresses, provider failure, uncertain sends, sender checks, the owner-only test email, duplicate triggers, concurrency, initialization and batch limits. They do not substitute for the live owner test and controlled signup test above.

Official references:

- [WorkOS waitlist API](https://workos.com/docs/reference/authkit/waitlist)
- [WorkOS waitlist behavior](https://workos.com/docs/authkit/waitlist)
- [Google MailApp](https://developers.google.com/apps-script/reference/mail/mail-app)
- [Google Apps Script quotas](https://developers.google.com/apps-script/guides/services/quotas)
- [Installable triggers](https://developers.google.com/apps-script/guides/triggers/installable)
