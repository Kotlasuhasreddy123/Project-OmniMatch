/** Auth utilities — token decode and session management. */

import { clearToken, setToken } from "@/lib/apiClient";
import type { UserRole } from "@/types";

interface TokenClaims {
  sub: string;
  role: UserRole;
  exp: number;
}

export function decodeToken(token: string): TokenClaims | null {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded) as TokenClaims;
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const claims = decodeToken(token);
  if (!claims) return true;
  return Date.now() / 1000 > claims.exp;
}

export function storeToken(token: string): void {
  setToken(token);
}

export function logout(): void {
  clearToken();
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

export function getCurrentUser(): TokenClaims | null {
  if (typeof window === "undefined") return null;
  const token = sessionStorage.getItem("omni_token");
  if (!token || isTokenExpired(token)) return null;
  return decodeToken(token);
}
