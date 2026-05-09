import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"

function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, "")
}

export function GET() {
  const config = {
    apiBaseUrl: trimTrailingSlash(process.env.API_BASE_URL || "http://localhost:8000"),
    supabaseUrl: process.env.SUPABASE_URL || "",
    supabaseAnonKey: process.env.SUPABASE_ANON_KEY || "",
  }

  return NextResponse.json(config, {
    headers: {
      "Cache-Control": "no-store",
    },
  })
}
