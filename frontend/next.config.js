/** @type {import('next').NextConfig} */
const nextConfig = {
  // An alternate output path allows verification when OneDrive locks an
  // earlier generated .next directory. Docker keeps the default .next path.
  distDir: process.env.OMNIMATCH_NEXT_DIST_DIR || ".next",
  // Standalone output required for Docker multi-stage build
  output: "standalone",

  // Skip ESLint during `next build` — ESLint runs separately via hooks and CI
  // This prevents linting warnings from blocking the Docker build
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Skip TypeScript type-check during build for speed (tsc runs separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
