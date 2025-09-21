/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'export', // Enable static export for Firebase Hosting
  trailingSlash: true, // Required for static export
  // Note: rewrites don't work with static export, API calls will go directly to NEXT_PUBLIC_BACKEND_URL
}

export default nextConfig
