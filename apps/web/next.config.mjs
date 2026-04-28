/** @type {import('next').NextConfig} */
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
    // Production builds (Vercel / ECS) talk to the API directly via
    // NEXT_PUBLIC_API_BASE_URL, so no rewrite is needed there.
    if (process.env.NODE_ENV !== 'development') return []
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ]
  },
}

export default nextConfig
