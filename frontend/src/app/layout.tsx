import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { PortalBoundary } from "@/components/PortalBoundary";

export const metadata: Metadata = {
  title: "OmniMatch — Ambient AI Clinical Trial Routing",
  description:
    "Consent-gated ambient audio capture with AI-powered clinical trial matching. CPSC-69100 Master's Project.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        {/* Skip navigation for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-blue-600 focus:px-4 focus:py-2 focus:text-white focus:shadow-lg"
        >
          Skip to main content
        </a>

        {/* Top navigation */}
        <nav
          className="border-b border-gray-200 bg-white shadow-sm"
          aria-label="Main navigation"
        >
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <div className="flex items-center gap-3">
              <span
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-sm"
                aria-hidden="true"
              >
                OM
              </span>
              <Link href="/" className="text-lg font-bold text-gray-900">OmniMatch</Link>
            </div>
            <nav className="flex flex-wrap gap-4 text-sm font-medium" aria-label="Site links">
              <Link href="/session" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                New Session
              </Link>
              <Link href="/inbox" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                Inbox
              </Link>
              <Link href="/timeline" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                Timeline
              </Link>
              <Link href="/models" className="text-gray-600 hover:text-blue-600">Models</Link>
              <Link href="/research" className="text-gray-600 hover:text-blue-600">Text & evidence</Link>
              <Link href="/validation" className="text-gray-600 hover:text-blue-600">Validation</Link>
              <Link href="/login" className="font-semibold text-teal-800">Access</Link>
            </nav>
          </div>
        </nav>

        {/* Main content */}
        <main id="main-content" className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          <PortalBoundary>{children}</PortalBoundary>
        </main>
        <footer className="mx-auto flex max-w-7xl flex-wrap justify-between gap-4 border-t px-6 py-7 text-sm text-gray-600"><span>OmniMatch · Synthetic-data research workspace</span><div className="flex flex-wrap gap-5"><Link href="/policies">Policies & privacy</Link><Link href="/licenses">Licenses</Link><a href="mailto:suhasreddykotla222@gmail.com">Contact / report a concern</a></div></footer>
      </body>
    </html>
  );
}
