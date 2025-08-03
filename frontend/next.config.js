/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Disable ESLint during builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript build errors (optional, for faster builds)
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig
