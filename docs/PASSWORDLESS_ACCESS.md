# Owner-approved email access

Owner and policy contact: suhasreddykotla222@gmail.com. No shared account password is used.

The application now requires WorkOS-signed account tokens. Blank settings intentionally disable sign-in. The source code and preview stay public under MIT; approval protects account/API access, not the ability to copy public source.

## Configure your free WorkOS application

1. Create a WorkOS AuthKit application. Enable Magic Auth (email codes) and disable password and social sign-in. Enable the native waitlist. Disable automatic verified-domain/JIT membership. Review any existing accounts separately: enabling a waitlist does not revoke existing users.
2. Create an organization for approved OmniMatch users. Create an access permission named `omnimatch:access` and an administrator permission named `omnimatch:admin`. A staff role receives access; an owner role receives both permissions.
3. Allow the browser origins `http://localhost:3000` and your GitHub Pages origin. Add the exact redirect URLs `http://localhost:3000/login/` and `https://Kotlasuhasreddy123.github.io/Project-OmniMatch/login/`. Add `http://localhost:3013/login/` and its origin only if using that development port. Configure matching logout destinations in the provider dashboard.
4. Put the public client ID and organization ID into `frontend/.env.local` as `NEXT_PUBLIC_WORKOS_CLIENT_ID` and `NEXT_PUBLIC_WORKOS_ORG_ID`. Put the same values into `backend/.env` as `WORKOS_CLIENT_ID` and `WORKOS_ORGANIZATION_ID`. Never put a WorkOS API secret into browser variables or GitHub source.
5. For Docker builds, also set `WORKOS_CLIENT_ID` and `WORKOS_ORGANIZATION_ID` in the root Compose `.env`, because browser settings are compiled into the image. Rebuild the frontend after changing them. These IDs are public identifiers, not passwords.
6. In the WorkOS dashboard, review each waitlist request. Approve only the intended user. Approval sends an invitation; the sign-in flow sends a separate short-lived email code. Ensure the approved person also has organization membership and the staff role. A waitlist approval alone does not grant API permissions.
7. For the public Pages build, set repository Actions variables `WORKOS_CLIENT_ID` and `WORKOS_ORGANIZATION_ID`, then rerun its deployment. Leave them blank until configured, as requested.

## Verify before opening registration

- Without a token, inbox requests return 401. A token from another application, an expired token, or an altered signature is rejected. A valid identity without the required organization/permission returns 403.
- An approved staff account can review synthetic visits. Only an account with the admin permission can use administrative endpoints.
- Test requesting access, denying access, approving an invitation, email-code expiry, sign-out, and membership removal using separate test accounts. These provider flows cannot be verified while application IDs are blank.
- Removing membership may not revoke an already-issued access token immediately. Revoke provider sessions and allow for access-token expiry. This verifier checks signed tokens, not a live revocation list on every request.

## Hosting and cost boundaries

GitHub Pages serves a noncommercial academic portal, sample results, policies, and installation links. It cannot run FastAPI, Whisper, Qdrant, or scheduled jobs. Those run on the user's local computer. No clinical recordings or visit notes belong on the public site.

The browser SDK uses its free browser mode and stores refresh state in browser storage. Treat shared computers accordingly and sign out. Do not enable paid custom domains, enterprise SSO, or paid email-domain options for this setup. Free-tier terms and limits can change; no service is guaranteed free forever. The Pages workflow publishes only the frontend's static output, never the backend, local databases, environment files or model caches. For a future commercial service, reassess hosting terms and use an appropriate application host.

References: [WorkOS waitlist](https://workos.com/docs/authkit/waitlist), [Magic Auth](https://workos.com/docs/authkit/magic-auth), [React/browser integration](https://workos.com/docs/authkit/react), [session tokens](https://workos.com/docs/reference/authkit/session-tokens), [pricing](https://workos.com/pricing), [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).
