"use client"

export interface RuntimeConfig {
  apiBaseUrl: string
  supabaseUrl: string
  supabaseAnonKey: string
}

let configPromise: Promise<RuntimeConfig> | null = null

function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, "")
}

async function fetchConfig(): Promise<RuntimeConfig> {
  const response = await fetch("/api/config", { cache: "no-store" })

  if (!response.ok) {
    throw new Error(`Unable to load runtime config: ${response.status}`)
  }

  const config = (await response.json()) as RuntimeConfig

  return {
    apiBaseUrl: trimTrailingSlash(config.apiBaseUrl || "http://localhost:8000"),
    supabaseUrl: config.supabaseUrl || "",
    supabaseAnonKey: config.supabaseAnonKey || "",
  }
}

export function getConfig() {
  if (!configPromise) {
    configPromise = fetchConfig().catch((error) => {
      configPromise = null
      throw error
    })
  }

  return configPromise
}
