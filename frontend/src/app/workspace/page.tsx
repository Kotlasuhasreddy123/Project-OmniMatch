"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { authClient, accessConfigured } from "@/lib/passwordless";
import { getCurrentUser, storeToken } from "@/lib/auth";
import { clearToken } from "@/lib/apiClient";

export default function WorkspacePage() {
  const [state, setState] = useState("Checking access…");
  const [approved, setApproved] = useState(false);
  const [admin, setAdmin] = useState(false);
  useEffect(() => {
    if (!accessConfigured) {
      setState("Account access is awaiting owner configuration.");
      return;
    }
    let active = true;
    authClient()
      .then(async (client) => {
        if (!client.getUser()) {
          if (active)
            setState(
              "Sign in with your approved email account to open the member workspace.",
            );
          return;
        }
        const token = await client.getAccessToken();
        if (!active) return;
        storeToken(token);
        const user = getCurrentUser();
        setApproved(Boolean(user));
        setAdmin(user?.role === "ADMIN");
        setState(
          user
            ? "Your account has a workspace access role."
            : "Your account is waiting for an organization access role.",
        );
      })
      .catch(() => {
        if (active)
          setState("Your session could not be verified. Sign in again.");
      });
    return () => {
      active = false;
    };
  }, []);
  return (
    <section className="mx-auto max-w-5xl space-y-6 py-8">
      <p className="eyebrow">MEMBER WORKSPACE</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        One account. A workspace on your computer.
      </h1>
      <p role="status" className="rounded-2xl bg-teal-50 p-5 text-teal-900">
        {state}
      </p>
      {approved ? (
        <>
          <div className="grid gap-5 sm:grid-cols-2">
            <article className="rounded-2xl border bg-white p-7">
              <h2 className="text-xl font-semibold">📦 Install OmniMatch</h2>
              <p className="my-4 leading-7 text-gray-600">
                Download the source and follow the local Docker guide. Models
                and synthetic visit information stay in your installation.
              </p>
              <a
                href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/archive/refs/heads/main.zip"
                className="text-teal-800 underline"
              >
                Download source ZIP
              </a>
              <br />
              <a
                href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/INSTALL_ON_YOUR_COMPUTER.md"
                className="mt-3 inline-block text-teal-800 underline"
              >
                Open installation guide →
              </a>
            </article>
            <article className="rounded-2xl border bg-indigo-50 p-7">
              <h2 className="text-xl font-semibold">🖥️ Open your local app</h2>
              <p className="my-4 leading-7 text-gray-600">
                Start Docker, open the app on localhost and sign in with the
                same approved identity. The local API independently checks your
                organization and permissions.
              </p>
              <a
                href="http://localhost:3000"
                className="text-indigo-900 underline"
              >
                Open installed workspace ↗
              </a>
            </article>
          </div>
          {admin && (
            <a
              href="https://dashboard.workos.com"
              className="inline-block rounded-full bg-slate-900 px-6 py-3 text-white"
            >
              Owner: review access requests in WorkOS ↗
            </a>
          )}
          <button
            onClick={async () => {
              clearToken();
              setApproved(false);
              const client = await authClient();
              await client.signOut();
            }}
            className="block rounded-full border bg-white px-6 py-3"
          >
            Sign out
          </button>
        </>
      ) : (
        <Link
          href="/login"
          className="inline-block rounded-full bg-teal-700 px-6 py-3 text-white"
        >
          Request access or sign in
        </Link>
      )}
      <p className="text-sm leading-6 text-gray-600">
        The public repository and its source license remain public regardless of
        account status. Clinical processing is available only in the local
        installation, with synthetic data.
      </p>
      <Link href="/validation" className="inline-block underline">
        Review validation coverage before use →
      </Link>
    </section>
  );
}
