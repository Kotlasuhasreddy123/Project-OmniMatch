/** @type {import('next').NextConfig} */
const nextConfig = {
  // An alternate output path allows verification when OneDrive locks an
  // earlier generated .next directory. Docker keeps the default .next path.
  distDir: process.env.OMNIMATCH_NEXT_DIST_DIR || ".next",
  // Standalone output required for Docker multi-stage build
  output: "standalone",

};

module.exports = nextConfig;
