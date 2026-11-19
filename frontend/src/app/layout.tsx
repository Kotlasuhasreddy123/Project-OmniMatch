import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { PortalBoundary } from "@/components/PortalBoundary";
import { SiteHeader } from "@/components/SiteHeader";
import { browserCsp } from '../../security-policy';

export const metadata: Metadata = {
  icons: { icon: { url: `${process.env.NEXT_PUBLIC_BASE_PATH || ""}/omnimatch-icon.svg`, type: "image/svg+xml" } },
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
      <head><meta httpEquiv="Content-Security-Policy" content={browserCsp()} /></head>
      <body className="min-h-screen font-sans antialiased">
        {/* Skip navigation for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-blue-600 focus:px-4 focus:py-2 focus:text-white focus:shadow-lg"
        >
          Skip to main content
        </a>

        <SiteHeader />

        {/* Main content */}
        <main id="main-content" className="app-main">
          <PortalBoundary>{children}</PortalBoundary>
        </main>
        <footer className="site-footer"><div><Link href="/" className="font-semibold text-slate-800">OmniMatch</Link><p className="mt-1">Academic research · Synthetic patient data only</p></div><nav aria-label="Footer navigation"><Link href="/guide">User guide</Link><Link href="/policies">Privacy & terms</Link><Link href="/licenses">Licenses</Link><a href="mailto:suhasreddykotla222@gmail.com">Contact</a></nav></footer>
      </body>
    </html>
  );
}
