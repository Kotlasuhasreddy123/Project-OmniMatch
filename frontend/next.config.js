/** @type {import('next').NextConfig} */
const { browserCsp } = require('./security-policy');
const nextConfig = {
  outputFileTracingRoot: __dirname,
  // An alternate output path allows verification when OneDrive locks an
  // earlier generated .next directory. Docker keeps the default .next path.
  distDir: process.env.OMNIMATCH_NEXT_DIST_DIR || ".next",
  // Standalone output required for Docker multi-stage build
  output: process.env.OMNIMATCH_STATIC_EXPORT === "true" ? "export" : "standalone",
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || "",
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
  async headers() {
    if (process.env.OMNIMATCH_STATIC_EXPORT === 'true') return [];
    return [{ source: '/:path*', headers: [
      { key: 'Content-Security-Policy', value: browserCsp() + "; frame-ancestors 'none'" },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      { key: 'Permissions-Policy', value: 'microphone=(self), camera=(), geolocation=()' },
    ] }];
  },

};

module.exports = nextConfig;
