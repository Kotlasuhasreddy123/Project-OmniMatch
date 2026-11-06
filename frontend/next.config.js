/** @type {import('next').NextConfig} */
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

};

module.exports = nextConfig;
