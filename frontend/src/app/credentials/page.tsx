"use client";
import { useState, FormEvent } from "react";
import Link from "next/link";
import { checkProfessionalRegistry, type RegistryResult } from "@/lib/apiClient";
import { portalMode } from "@/lib/passwordless";

export default function CredentialsPage() {
  const [npi, setNpi] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<RegistryResult | null>(null);
  const [error, setError] = useState("");
  async function lookup(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setResult(null);
    try { setResult(await checkProfessionalRegistry(npi)); }
    catch (err) { setError(err instanceof Error ? err.message : "Lookup unavailable. Try again later."); }
    finally { setBusy(false); }
  }
  return <section className="mx-auto max-w-2xl space-y-6">
    <p className="eyebrow">PROFESSIONAL REGISTRY</p>
    <h1 className="text-3xl font-semibold tracking-tight">Check a U.S. NPI record</h1>
    <p className="leading-7 text-gray-600">Find an individual provider record in the official CMS registry. This lookup supports owner review; it does not verify that you are the person listed, confirm a medical license, or unlock an account.</p>
    {portalMode ? <div className="rounded-2xl border border-teal-200 bg-teal-50 p-6 leading-7"><h2 className="font-semibold">Use the official registry on this public site</h2><p>The built-in check runs in your installed OmniMatch application. On this public portal, open the official CMS registry using the link below.</p><a href="https://npiregistry.cms.hhs.gov/" target="_blank" rel="noreferrer" className="mt-3 inline-block font-semibold underline">Open the CMS registry ↗</a></div> : <form onSubmit={lookup} className="space-y-4 rounded-2xl border bg-white p-6">
      <label htmlFor="npi" className="block font-semibold">10-digit NPI number</label>
      <input id="npi" inputMode="numeric" pattern="[12][0-9]{9}" minLength={10} maxLength={10} required value={npi} onChange={e => { setNpi(e.target.value.replace(/\D/g, "")); setResult(null); setError(""); }} aria-describedby="npi-help" className="w-full rounded-xl border border-gray-300 p-3 focus-visible:ring-2 focus-visible:ring-teal-600" />
      <p id="npi-help" className="text-sm leading-6 text-gray-600">Selecting Check record sends only this number to CMS through the OmniMatch backend. No name, phone number or ID-card upload is required, and no professional profile is saved.</p>
      <button disabled={busy || npi.length !== 10} className="rounded-full bg-teal-800 px-6 py-3 font-medium text-white disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2">{busy ? "Checking registry…" : "Check record"}</button>
    </form>}
    {error && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-900">{error}</p>}
    {result && <div role="status" className="space-y-2 rounded-2xl border border-sky-200 bg-sky-50 p-6 text-sky-950">
      <h2 className="text-xl font-semibold">{result.status === "record_found" ? "Registry record found — identity not verified" : "Owner review needed"}</h2>
      {result.registry_name && <p className="font-medium">{result.registry_name}</p>}
      {result.specialty && <p>{result.specialty}</p>}
      <p className="leading-6">{result.message}</p>
      <p className="text-sm">Account access: unchanged. No account has been created using this record.</p>
    </div>}
    <div className="rounded-2xl bg-gray-100 p-5 text-sm leading-6"><h2 className="font-semibold">Outside the United States?</h2><p>Professional registers differ by country. Ask the workspace owner to review your institution and the relevant licensing authority. Worldwide automatic verification is not available.</p></div>
    <div className="flex flex-wrap gap-5 text-sm"><Link href="/login" className="font-medium text-teal-800 underline">Return to sign in</Link><a href="https://npiregistry.cms.hhs.gov/" target="_blank" rel="noreferrer" className="underline">Official CMS registry ↗</a></div>
  </section>;
}
