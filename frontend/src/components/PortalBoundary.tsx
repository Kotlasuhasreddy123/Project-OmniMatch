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
      <section className="ui-panel mx-auto max-w-3xl">
        <p className="eyebrow">LOCAL WORKSPACE REQUIRED</p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight">
          Open your local research workspace
        </h1>
        <p className="my-5 max-w-2xl leading-7">
          Recording, study matching and saved visits run in the installed app. This public website provides examples, setup guides and account access. If you have already started the local services, open your workspace below.
        </p>
        <div className="flex flex-wrap gap-4">
          <a
            href="http://localhost:3000"
            className="ui-button"
          >
            Open installed app ↗
          </a>
          <Link href="/workspace" className="ui-button ui-button-secondary">
            Installation and access
          </Link>
          <Link href="/preview" className="ui-link">
            View example results
          </Link>
        </div>
      </section>
    );
  }
  return <>{children}</>;
}
