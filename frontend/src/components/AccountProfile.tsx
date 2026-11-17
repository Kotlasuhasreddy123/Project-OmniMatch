"use client";

import { useEffect, useState } from "react";
import { authClient, accessConfigured } from "@/lib/passwordless";
import { getCurrentUser } from "@/lib/auth";

export function AccountProfile() {
  const [profile, setProfile] = useState<{ email: string; name: string; role: string } | null>(null);
  useEffect(() => {
    let active = true;
    const update = async () => {
      if (!accessConfigured) return;
      try {
        const user = (await authClient()).getUser();
        const claims = getCurrentUser();
        if (active) setProfile(user && claims ? {
          email: user.email,
          name: [user.firstName, user.lastName].filter(Boolean).join(" ") || user.email,
          role: claims.role === "ADMIN" ? "Owner" : "Clinical staff",
        } : null);
      } catch { if (active) setProfile(null); }
    };
    void update();
    window.addEventListener("omni-auth-change", update);
    return () => { active = false; window.removeEventListener("omni-auth-change", update); };
  }, []);
  if (!profile) return null;
  return <details className="relative">
    <summary aria-label={`Signed in as ${profile.email}`} title={profile.email} className="flex h-9 w-9 cursor-pointer list-none items-center justify-center rounded-full bg-teal-800 font-bold text-white focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2">
      {profile.name.slice(0, 1).toUpperCase()}
    </summary>
    <div className="absolute right-0 z-50 mt-3 w-72 rounded-2xl border bg-white p-4 text-sm shadow-lg">
      <p className="font-semibold text-gray-900">{profile.name}</p>
      <p className="mt-1 break-all text-gray-600">{profile.email}</p>
      <p className="mt-2 text-teal-800">{profile.role} · Personal workspace</p>
      <p className="mt-2 text-xs text-gray-600">Your saved visits and patient history are private to your account.</p>
    </div>
  </details>;
}
