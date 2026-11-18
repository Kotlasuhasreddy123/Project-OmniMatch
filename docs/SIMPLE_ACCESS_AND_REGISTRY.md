# Sign-in and professional registry checks

## What the user does

1. Open Sign in and verify their email with WorkOS.
2. New accounts need one owner approval. Keep the pending page open; it refreshes permissions every 15 seconds while visible.
3. After approval, the page opens the workspace automatically. Returning users with an active provider session are routed directly to their workspace.
4. A new email code is needed when the provider session ends. Approval does not need to be repeated unless revoked.

The owner still approves membership with the **OmniMatch Clinical Staff** role in WorkOS. The application does not turn a public registry match into an access permission. Each account retains its own private inbox and patient history.

## Optional U.S. registry check

Open `/credentials/`, enter a 10-digit NPI, then select **Check record**. The backend checks the check digit and queries the official CMS NPPES API v2.1 over HTTPS. It returns only the public provider name, primary specialty and record status. It does not return addresses or phone numbers, save a professional profile, create a user, or grant permissions.

No new paid service or API key is used. Existing WorkOS and hosting limits still apply. The public website is a static portal; the lookup requires a running backend, just like visit processing.

## What is not automated

A designation, hospital name, phone number, ID-card image or public physician number does not prove that the applicant owns that identity. NPI issuance also does not confirm licensure or credentials. Outside the U.S., the relevant country and licensing authority must be reviewed separately. Worldwide automatic physician verification is not implemented.

For this academic system, we do not collect ID-card images or phone numbers to claim professional verification. Do not register using another physician's public identity. Test account registration with synthetic identities or consenting users; public records may be queried separately as read-only integration tests.

## Tests and sources

- Synthetic tests cover active, inactive, organization and missing records; invalid numbers; registry outage; malformed responses; size limits; and no access being granted after lookup.
- Authentication and account-isolation tests remain separate from registry lookup.
- A read-only live CMS search returned an individual NPI record on November 17, 2026. No account was created and no privileges were assigned using that record.
- CMS registry: https://npiregistry.cms.hhs.gov/
- Official API: https://npiregistry.cms.hhs.gov/api-page
- WorkOS session lifecycle: https://workos.com/docs/authkit/sessions
