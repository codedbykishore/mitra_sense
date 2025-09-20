"use client"
import { LogOut } from "lucide-react"

export default function LogoutButton() {
  const handleLogout = async () => {
    try {
      // Call your FastAPI logout endpoint
      await fetch("http://localhost:8000/logout", {
        method: "GET",
        credentials: "include", // include cookies/session  /google/login
      })

      // Refresh the page or redirect to homepage/login
      window.location.href = "/"
    } catch (err) {
      console.error("Logout failed:", err)
    }
  }

  return (
    <button
      onClick={handleLogout}
      className="flex items-center gap-3 w-full p-2 text-sm text-left text-red-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg"
    >
      <LogOut className="h-4 w-4" />
      <span>Log out</span>
    </button>
  )
}
