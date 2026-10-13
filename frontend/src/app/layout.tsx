import type { Metadata } from "next";
import "./globals.css";

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
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
            <div className="flex items-center gap-3">
              <span
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-sm"
                aria-hidden="true"
              >
                OM
              </span>
              <span className="text-lg font-bold text-gray-900">OmniMatch</span>
            </div>
            <nav className="flex gap-4 text-sm font-medium" aria-label="Site links">
              <a href="/session" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                New Session
              </a>
              <a href="/inbox" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                Inbox
              </a>
              <a href="/timeline" className="text-gray-600 hover:text-blue-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded">
                Timeline
              </a>
            </nav>
          </div>
        </nav>

        {/* Main content */}
        <main id="main-content" className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          {children}
        </main>
      </body>
    </html>
  );
}
