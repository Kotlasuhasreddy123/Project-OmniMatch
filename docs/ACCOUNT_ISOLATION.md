# Personal workspaces

Each signed-in account owns its visits. Membership in the same WorkOS organization does not share records. Owner privileges allow administration, but do not bypass visit ownership.

- Inbox lists, individual records, review, archive, restore and referrals check the authenticated account ID on the server.
- Timeline searches use only that account's saved visits. Two accounts can use the same synthetic patient ID without combining histories.
- A session ID belongs to the first authenticated account that creates it. Another account cannot reuse it.
- Switching accounts clears the previous account's local visit drafts and patient labels.
- The round profile icon shows the signed-in email and role.

Existing records are not deleted. The migration recovers an owner only when the historical audit trail identifies exactly one account. Unattributed or ambiguous records remain stored but hidden. There is no automatic claim or transfer of these records.

## Verify with two accounts

1. Open account A and account B in separate browser profiles.
2. Create one synthetic visit in each, using the same patient ID, such as DEMO-ISOLATION.
3. Approve different terms and submit each visit.
4. Each inbox and timeline should show only its own visit.
5. A record URL copied from the other account must return not found.
6. Open the profile icon and confirm the expected email.

Automated coverage is in `backend/tests/test_account_isolation.py` and `frontend/src/__tests__/AccountProfile.test.tsx`.
