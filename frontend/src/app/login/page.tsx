"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  accessConfigured,
  authClient,
  organizationId,
  portalMode,
} from "@/lib/passwordless";
import { storeToken, getCurrentUser } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [error, setError] = useState("");
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
        else
          setError(
            "Your email is verified. The owner still needs to grant your organization access role.",
          );
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
      <p className="eyebrow">ACCESS BY APPROVAL</p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">
        Your email. Your invitation.
        <br />
        No shared passwords.
      </h1>
      <p className="mt-5 max-w-2xl leading-7 text-gray-600">
        Request access first. The owner reviews requests in WorkOS. Approval
        sends an invitation, and approved members can sign in with a one-time
        email code.
      </p>
      <div className="my-8 grid gap-4 sm:grid-cols-3">
        {[
          [
            "01",
            "Request access",
            "Submit your email on the provider’s waitlist.",
          ],
          [
            "02",
            "Owner review",
            "The owner approves your invitation and organization role.",
          ],
          [
            "03",
            "Email code",
            "Follow the invitation and verify your email with WorkOS.",
          ],
        ].map(([n, title, text]) => (
          <div key={n} className="rounded-2xl border bg-white p-6">
            <span className="text-xl font-semibold text-teal-700">{n}</span>
            <h2 className="my-2 font-semibold">{title}</h2>
            <p className="text-sm leading-6 text-gray-600">{text}</p>
          </div>
        ))}
      </div>
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
      <label className="flex items-start gap-3 text-sm leading-6">
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
      </label>
      {error && (
        <p
          role="alert"
          className="mt-4 rounded-xl bg-rose-50 p-4 text-rose-800"
        >
          {error}
        </p>
      )}
      <div className="mt-6 flex flex-wrap gap-4">
        <button
          disabled={!accessConfigured || !accepted || busy}
          onClick={() => begin(true)}
          className="rounded-full bg-teal-700 px-6 py-3 font-medium text-white disabled:opacity-40"
        >
          Request access
        </button>
        <button
          disabled={!accessConfigured || !accepted || busy}
          onClick={() => begin(false)}
          className="rounded-full border bg-white px-6 py-3 font-medium disabled:opacity-40"
        >
          Approved? Sign in with email code
        </button>
        <Link href="/preview" className="px-4 py-3 underline">
          Explore sample results
        </Link>
      </div>
      <p className="mt-6 text-sm leading-6 text-gray-600">
        GitHub source is public under its license. Account approval controls the
        official workspace; it cannot prevent downloading or modifying public
        source code.
      </p>
    </section>
  );
}
