"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, ArrowUpRight } from "lucide-react";
import { AccountProfile } from "./AccountProfile";
import { portalMode } from "@/lib/passwordless";

export function SiteHeader() {
  const path = (usePathname() || "/").replace(/\/$/, "") || "/";
  const [open, setOpen] = useState(false);
  const links = portalMode
    ? [["/", "Overview"], ["/preview", "Sample results"], ["/guide", "Setup guide"]]
    : [["/session", "New visit"], ["/inbox", "Inbox"], ["/timeline", "Patient history"], ["/research", "Analyze a note"]];
  const resources = [["/models", "AI & data"], ["/validation", "Test results"], ["/credentials", "Professional registry"], ...(!portalMode ? [["/guide", "Setup guide"], ["/preview", "Sample results"]] : [])];
  return <header className="site-header">
    <div className="header-inner">
      <Link href="/" aria-label="OmniMatch home" className="brand" onClick={() => setOpen(false)}><span className="brand-mark" aria-hidden="true">om</span><span>OmniMatch<span className="brand-caption">Clinical research workspace</span></span></Link>
      <button className="mobile-menu" aria-expanded={open} aria-controls="site-navigation" aria-label={open ? "Close navigation" : "Open navigation"} onClick={() => setOpen(!open)}>{open ? <X size={21} /> : <Menu size={21} />}</button>
      <nav id="site-navigation" className={`site-navigation ${open ? "is-open" : ""}`} aria-label="Main navigation">
        {links.map(([href, label]) => <Link key={href} href={href} aria-current={path === href ? "page" : undefined} className="nav-link" onClick={() => setOpen(false)}>{label}</Link>)}
        <details className="resource-menu" key={path}><summary className="nav-link" aria-current={resources.some(([href]) => href === path) ? "true" : undefined}>Resources <span aria-hidden="true">⌄</span></summary><div className="resource-popover">{resources.map(([href, label]) => <Link key={href} href={href} aria-current={path === href ? "page" : undefined} onClick={() => setOpen(false)}>{label}</Link>)}</div></details>
        <Link href="/login" className="ui-button ui-button-small" aria-current={path === "/login" || path === "/workspace" ? "page" : undefined} onClick={() => setOpen(false)}>Account access <ArrowUpRight size={15} aria-hidden="true" /></Link>
        <AccountProfile />
      </nav>
    </div>
  </header>;
}
