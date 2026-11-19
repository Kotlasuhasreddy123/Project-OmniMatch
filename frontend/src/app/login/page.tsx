"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  accessConfigured,
  authClient,
  organizationId,
  portalMode,
} from "@/lib/passwordless";
import { storeToken, getCurrentUser } from "@/lib/auth";
import { clearToken } from "@/lib/apiClient";
import { PublicResources } from "@/components/PublicResources";

export default function LoginPage() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [newUser, setNewUser] = useState(false);
  const [error, setError] = useState("");
  const [accessPending, setAccessPending] = useState(false);
  const approvalInFlight = useRef(false);
  useEffect(() => {
    if (!accessConfigured) return;
    let active = true;
    authClient()
      .then(async (client) => {
        if (!client.getUser()) return;
        const token = await client.getAccessToken();
        if (!active) return;
        storeToken(token);
        if (getCurrentUser())
          router.replace(portalMode ? "/workspace" : "/session");
        else {
          clearToken();
          setAccessPending(true);
        }
      })
      .catch((err) => {
        if (active)
          setError(
            err instanceof Error
              ? err.message
              : "Sign-in could not be completed.",
          );
      });
    return () => {
      active = false;
    };
  }, [router]);

  const checkApproval = useCallback(async () => {
    if (approvalInFlight.current) return;
    approvalInFlight.current = true;
    setBusy(true);
    setError("");
    try {
      const client = await authClient();
      storeToken(await client.getAccessToken({ forceRefresh: true }));
      if (getCurrentUser()) router.replace(portalMode ? "/workspace" : "/session");
      else { clearToken(); setAccessPending(true); }
    } catch {
      setError("We could not check your approval. Try again, or sign in with your approved email.");
    } finally { approvalInFlight.current = false; setBusy(false); }
  }, [router]);

  useEffect(() => {
    if (!accessPending) return;
    const interval = window.setInterval(() => { if (document.visibilityState === "visible") void checkApproval(); }, 15000);
    return () => window.clearInterval(interval);
  }, [accessPending, checkApproval]);

  const begin = async (requestAccess: boolean) => {
    setBusy(true);
    setError("");
    try {
      const client = await authClient();
      if (requestAccess) await client.signUp({ organizationId });
      else await client.signIn({ organizationId });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The identity provider could not be opened.",
      );
      setBusy(false);
    }
  };
  return <>
    <section className="access-layout" aria-labelledby="access-title">
      <div className="access-intro">
        <p className="eyebrow">Account access</p>
        <h1 id="access-title">Your own workspace.<br />One owner approval.</h1>
        <p>Sign in with your email to work with visits, study suggestions and patient history in your installed application.</p>
        <ol className="access-steps" aria-label="Account access steps">
          <li><span className="step-number">1</span><div><strong>Verify your email</strong><p>Use the one-time code sent by WorkOS.</p></div></li>
          <li><span className="step-number">2</span><div><strong>Receive owner approval</strong><p>For new requests, check your email for a professional-details request.</p></div></li>
          <li><span className="step-number">3</span><div><strong>Open your personal workspace</strong><p>Your inbox and saved visits remain separate from other accounts.</p></div></li>
        </ol>
      </div>
      <div className="access-card">
        {accessPending ? <section role="status" aria-labelledby="approval-pending-heading">
          <p className="eyebrow">Email verified</p>
          <h2 id="approval-pending-heading" className="mt-3 text-xl font-semibold tracking-tight">Workspace approval pending</h2>
          <p className="mt-3 text-sm leading-7 text-slate-600">The owner needs to approve this account once. We check every 15 seconds while this page is open and take you to your workspace when access is ready.</p>
          <button onClick={checkApproval} disabled={busy} className="ui-button mt-5 w-full">{busy ? "Checking approval…" : "Check now"}</button>
          <p className="mt-4 text-xs leading-6 text-slate-600">Already approved? The owner should confirm your active membership and Clinical Staff role in WorkOS.</p>
        </section> : <>
          <div className="access-modes" role="group" aria-label="Choose account access">
            <button aria-pressed={!newUser} onClick={() => {setNewUser(false); setError("");}}>Sign in</button>
            <button aria-pressed={newUser} onClick={() => {setNewUser(true); setError("");}}>New user</button>
          </div>
          <h2 className="text-xl font-semibold tracking-tight">{newUser ? "Request your account" : "Welcome back"}</h2>
          <p className="mt-2 text-sm leading-7 text-slate-600">{newUser ? "Verify your email, then provide your professional details for the owner to review." : "Continue with your approved email. No password is needed."}</p>
          <label className="mt-6 flex items-start gap-3 text-xs leading-6 text-slate-600">
            <input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} className="mt-1.5 h-4 w-4 shrink-0 accent-teal-700" />
            <span>I agree to the <Link href="/policies" className="underline underline-offset-2 text-slate-800">terms, privacy notice and acceptable use rules</Link> and will use synthetic patient data only.</span>
          </label>
          <button disabled={!accessConfigured || !accepted || busy} onClick={() => begin(newUser)} className="ui-button mt-5 w-full">{busy ? "Opening sign-in…" : newUser ? "Request access" : "Continue with email"}</button>
          <p className="mt-4 text-xs leading-6 text-slate-500">An active sign-in session opens your workspace automatically. A new email code is needed when that session ends.</p>
        </>}
        {!accessConfigured && <p role="status" className="status-note mt-4">Access requests are not open yet. The installation owner needs to configure account access. Public resources are available below.</p>}
        {error && <div role="alert" className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">{error}{accessPending && <button onClick={() => begin(false)} disabled={busy} className="mt-2 block font-semibold underline">Sign in again</button>}</div>}
        <div className="mt-6 border-t border-slate-100 pt-4 text-xs leading-6 text-slate-600">Need help? <a href="mailto:suhasreddykotla222@gmail.com" className="text-teal-800 underline underline-offset-2">Contact the workspace owner</a>.</div>
      </div>
    </section>
    <div className="mx-auto max-w-5xl border-t border-slate-200 pt-7"><PublicResources /></div>
  </>;
}
