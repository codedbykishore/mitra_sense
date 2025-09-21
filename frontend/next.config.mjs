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
  output: 'standalone', // Enable standalone output for Docker
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
      // Auth endpoints that are not under /api/v1/
      {
        source: '/logout',
        destination: `${backendUrl}/logout`,
      },
      {
        source: '/me',
        destination: `${backendUrl}/me`,
      },
      {
        source: '/google/login',
        destination: `${backendUrl}/google/login`,
      },
      {
        source: '/auth/google/callback',
        destination: `${backendUrl}/auth/google/callback`,
      },
    ];
  },
}

export default nextConfig
