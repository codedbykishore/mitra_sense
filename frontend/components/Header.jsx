"use client"
import { Brain } from "lucide-react"
import MobileNavMenu from "./MobileNavMenu"

export default function Header() {
  // Note: This component is kept for potential future use but is currently unused
  // Navigation is now handled by the sidebar only

  return (
    <div className="sticky top-0 z-30 flex items-center justify-between border-b border-zinc-200/60 bg-white/80 px-4 py-3 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/70">
      {/* MITRA Logo/Brand */}
      <div className="flex items-center gap-2">
        <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        <span className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          MITRA
        </span>
      </div>

      {/* Mobile Navigation Menu - Fallback option */}
      <div className="flex items-center gap-2 md:hidden">
        <MobileNavMenu />
      </div>
    </div>
  )
}
