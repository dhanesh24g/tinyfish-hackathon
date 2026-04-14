"use client"

import { Brain } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "./theme-toggle"

export function SiteHeader() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="container flex h-14 items-center justify-between px-4">
        <Link href="/interview" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <span className="font-semibold text-foreground hidden sm:inline">
            AI Interview Agent
          </span>
        </Link>
        
        <div className="flex items-center gap-4">
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <Link 
              href="https://www.dhaneshlabs.com/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              Dhanesh Labs
            </Link>
            <Link 
              href="https://www.dhaneshlabs.com/products" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              Products
            </Link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
