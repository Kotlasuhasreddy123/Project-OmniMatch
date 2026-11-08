"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";

export function PortalBoundary({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const localOnly = ["/session", "/verify", "/inbox", "/timeline", "/research"].some(
    (route) => path === route || path === `${route}/`,
  );
  if (process.env.NEXT_PUBLIC_PORTAL_MODE === "true" && localOnly) {
    return (
      <section className="rounded-3xl bg-teal-50 p-8">
        <p className="eyebrow">YOUR DATA STAYS WITH YOUR INSTALLATION</p>
        <h1 className="mt-4 text-3xl font-semibold">
          Open your local research workspace
        </h1>
        <p className="my-5 max-w-2xl leading-7">
          This public site handles access information and setup guides.
          Recording, extraction and study matching run on your own computer.
          Install the app, then open the local workspace and sign in with your
          approved account.
        </p>
        <div className="flex flex-wrap gap-4">
          <a
            href="http://localhost:3000"
            className="rounded-full bg-teal-700 px-5 py-3 text-white"
          >
            Open installed app ↗
          </a>
          <Link href="/workspace" className="rounded-full border px-5 py-3">
            Installation and access
          </Link>
          <Link href="/preview" className="px-5 py-3 underline">
            View example results
          </Link>
        </div>
      </section>
    );
  }
  return <>{children}</>;
}
