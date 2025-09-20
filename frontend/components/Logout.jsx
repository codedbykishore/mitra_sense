"use client"
import { LogOut } from "lucide-react"
import { useState } from "react"
import { apiService } from '../lib/api'

export default function LogoutButton() {
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    if (isLoggingOut) return // Prevent multiple clicks

    setIsLoggingOut(true)
    
    try {
      // Clear all cached data before logout
      apiService.clearCacheByPattern('conversations_')
      apiService.clearCacheByPattern('messages_')
      
      // Call FastAPI logout endpoint via Next.js proxy
      const response = await fetch("/logout", {
        method: "GET",
        credentials: "include", // include cookies/session
      })

      // Always reload the page to clear all state and redirect
      // This is the most reliable way to handle logout
      window.location.href = "/"
    } catch (err) {
      console.error("Logout failed:", err)
      // Clear cache even on error
      apiService.clearCacheByPattern('conversations_')
      apiService.clearCacheByPattern('messages_')
      // Force reload even if there's a network error
      window.location.href = "/"
    }
  }

  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      className="flex items-center gap-3 w-full p-2 text-sm text-left text-red-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <LogOut className="h-4 w-4" />
      <span>{isLoggingOut ? "Logging out..." : "Log out"}</span>
    </button>
  )
}
