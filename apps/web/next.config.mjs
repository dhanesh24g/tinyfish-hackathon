/** @type {import('next').NextConfig} */
const apiBaseUrl = (process.env.API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

const nextConfig = {
  output: 'standalone',
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    // Local dev convenience: proxy /api/* to the FastAPI server on :8000.
    // Production builds (Vercel / ECS / Cloud Run) load API_BASE_URL at runtime
    // through /api/config, so no rewrite is needed there.
    if (process.env.NODE_ENV !== 'development') return []
    return [
      {
        source: '/api/:path*',
        destination: `${apiBaseUrl}/:path*`,
      },
    ]
  },
}

export default nextConfig
