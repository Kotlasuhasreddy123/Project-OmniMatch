"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { authClient, accessConfigured } from "@/lib/passwordless";
import { getCurrentUser, storeToken } from "@/lib/auth";
import { clearToken } from "@/lib/apiClient";
import { PublicResources } from "@/components/PublicResources";

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
            : "Your email is verified. Workspace access is waiting for owner approval. Public resources remain available below.",
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
  return <section className="mx-auto max-w-4xl space-y-6">
    <header className="page-header"><p className="eyebrow">Account & installation</p><h1>{approved ? "Your account is ready." : "Open your workspace."}</h1><p>Use your approved account in your local OmniMatch installation. The public site provides examples and setup information.</p></header>
    <p role="status" className="status-note">{state}</p>
    {approved ? <>
      <div className="grid gap-5 sm:grid-cols-2">
        <article className="ui-panel"><span className="step-number">1</span><h2 className="mt-4 text-lg font-semibold">Install OmniMatch</h2><p className="mt-2 text-sm leading-7 text-slate-600">Download the source and follow the Docker setup guide. Models and saved visit information run in your installation.</p><a href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/INSTALL_ON_YOUR_COMPUTER.md" className="ui-link mt-4">Read the installation guide →</a><a href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/archive/refs/heads/main.zip" className="ui-link mt-3 block">Download source ZIP</a></article>
        <article className="ui-panel"><span className="step-number">2</span><h2 className="mt-4 text-lg font-semibold">Open the installed app</h2><p className="mt-2 text-sm leading-7 text-slate-600">Start Docker, then open the app on your computer. Sign in with the same approved email to reach your personal visits.</p><a href="http://localhost:3000" className="ui-button mt-5">Open local workspace ↗</a><p className="mt-3 text-xs leading-6 text-slate-500">This link works after the local services have started.</p></article>
      </div>
      <div className="flex flex-wrap items-center gap-4 border-t border-slate-200 pt-5">
        {admin && <a href="https://dashboard.workos.com" className="ui-button ui-button-secondary">Review access requests ↗</a>}
        <button onClick={async () => {clearToken(); setApproved(false); const client = await authClient(); await client.signOut();}} className="ui-link">Sign out</button>
      </div>
    </> : <><Link href="/login" className="ui-button">Continue to account access</Link><div className="pt-4"><PublicResources /></div></>}
  </section>;
}
