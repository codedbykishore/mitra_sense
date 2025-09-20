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
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
      // Auth endpoints that are not under /api/v1/
      {
        source: '/logout',
        destination: 'http://localhost:8000/logout',
      },
      {
        source: '/me',
        destination: 'http://localhost:8000/me',
      },
      {
        source: '/google/login',
        destination: 'http://localhost:8000/google/login',
      },
      {
        source: '/auth/google/callback',
        destination: 'http://localhost:8000/auth/google/callback',
      },
    ];
  },
}

export default nextConfig
