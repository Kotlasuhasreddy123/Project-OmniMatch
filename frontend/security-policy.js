/** Baseline CSP for SSR and static Pages. Inline Next hydration is still allowed. */
function browserCsp() {
  let apiOrigin = 'http://localhost:8000';
  try { apiOrigin = new URL(process.env.NEXT_PUBLIC_API_URL || apiOrigin).origin; } catch {}
  const development = process.env.NODE_ENV === 'development';
  return [
    "default-src 'self'", "base-uri 'self'", "object-src 'none'",
    "script-src 'self' 'unsafe-inline'" + (development ? " 'unsafe-eval'" : ''),
    "style-src 'self' 'unsafe-inline'", "img-src 'self' data:",
    "font-src 'self' data:",
    `connect-src 'self' ${apiOrigin} https://api.workos.com https://*.authkit.app` + (development ? ' ws://localhost:* ws://127.0.0.1:*' : ''),
    "frame-src https://*.authkit.app", "form-action 'self' https://*.authkit.app",
  ].join('; ');
}
module.exports = { browserCsp };
