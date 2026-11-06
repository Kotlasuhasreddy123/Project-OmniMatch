# Security and account incident procedure

Report suspected account misuse or data exposure to suhasreddykotla222@gmail.com. Include the time, affected page/version and a brief description. Do not email passwords, tokens, recordings, or patient details.

1. The owner records the report and assesses the affected account, installation and public version.
2. Stop the affected local service or public registration if needed. Revoke affected WorkOS sessions, remove organization membership, and rotate exposed secrets. Preserve minimal relevant logs without copying audio or patient information.
3. Identify the cause, affected records, timeframe and any third-party involvement. Account-token expiry means membership changes alone may not immediately terminate existing tokens.
4. Correct the issue, add a regression test, and verify the corrected version before restoring access.
5. Inform affected users and relevant providers where appropriate. Determine any notification duties with qualified advice. This procedure does not establish HIPAA, GDPR or other legal certification.
6. Record the resolution and changes needed to prevent recurrence. Local owners remain responsible for their own stored records, backups and deletion.

Only fictional patient information is permitted. No automated clinical safety classifier or complete content-moderation service is installed. Human review remains mandatory.
