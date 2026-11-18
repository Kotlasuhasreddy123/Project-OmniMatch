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
  return (
    <section className="mx-auto max-w-4xl py-8">
      <p className="eyebrow">YOUR PRIVATE WORKSPACE</p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">Sign in and start a visit.</h1>
      <p className="mt-4 max-w-2xl leading-7 text-gray-600">Approval is needed once per account. After approval, your existing sign-in session opens your workspace automatically. You only need a new email code when the sign-in session has ended.</p>
      <div className="my-6 rounded-2xl border border-teal-200 bg-teal-50 p-5 text-sm leading-6 text-teal-950">
        <strong>What happens next?</strong> Verify your email, receive one owner approval, then open your personal visits. Your inbox and patient history stay separate from other users.
      </div>
      {accessPending && (
        <section role="status" aria-labelledby="approval-pending-heading" className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-950">
          <h2 id="approval-pending-heading" className="font-semibold">Email verified — workspace approval pending</h2>
          <p className="mt-2 text-sm leading-6">You have finished signing in. The owner needs to approve this account once. Leave this page open: we check automatically every 15 seconds and open your workspace when approval is ready.</p>
          <button onClick={checkApproval} disabled={busy} className="mt-4 rounded-full border border-amber-400 bg-white px-4 py-2 text-sm font-medium disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-amber-700">{busy ? "Checking…" : "Check now"}</button>
        </section>
      )}
      {!accessConfigured && (
        <p
          role="status"
          className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900"
        >
          Access requests are not open yet. The owner must configure WorkOS and
          enable waitlist approvals and email codes. Preview and documentation
          remain available.
        </p>
      )}
      {!accessPending && <label className="flex items-start gap-3 text-sm leading-6">
        <input
          type="checkbox"
          checked={accepted}
          onChange={(e) => setAccepted(e.target.checked)}
          className="mt-1"
        />{" "}
        <span>
          I have read the{" "}
          <Link href="/policies" className="underline">
            terms, privacy notice and acceptable use rules
          </Link>
          . I will use synthetic data only.
        </span>
      </label>}
      {error && (
        <p
          role="alert"
          className="mt-4 rounded-xl bg-rose-50 p-4 text-rose-800"
        >
          {error}
          {accessPending && <button onClick={() => begin(false)} disabled={busy} className="ml-3 font-semibold underline">Sign in again</button>}
        </p>
      )}
      {!accessPending && <div className="mt-6 flex flex-wrap gap-4">
        <button
          disabled={!accessConfigured || !accepted || busy}
          onClick={() => begin(false)}
          className="rounded-full bg-teal-700 px-6 py-3 font-medium text-white disabled:opacity-40"
        >
          Continue with email
        </button>
        <button
          disabled={!accessConfigured || !accepted || busy}
          onClick={() => begin(true)}
          className="rounded-full border bg-white px-6 py-3 font-medium disabled:opacity-40"
        >
          Request access
        </button>
        <Link href="/preview" className="px-4 py-3 underline">
          Explore sample results
        </Link>
      </div>}
      <p className="mt-4 text-sm text-gray-600">Need professional credential information? <Link href="/credentials" className="font-medium text-teal-800 underline">Check a U.S. NPI record</Link>. Registry lookup does not approve an account.</p>
      <div className="mt-8"><PublicResources /></div>
      <p className="mt-6 text-sm leading-6 text-gray-600">
        GitHub source is public under its license. Account approval controls the
        official workspace; it cannot prevent downloading or modifying public
        source code.
      </p>
    </section>
  );
}
