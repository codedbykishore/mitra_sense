"use client"
import { LogIn } from "lucide-react"

export default function LoginButton() {
  const handleLogin = () => {
    // Use backend URL directly for Firebase Hosting deployment
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    window.location.href = `${backendUrl}/google/login`;
  }

  return (
    <button
      onClick={handleLogin}
      className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      <LogIn className="h-4 w-4" /> Login with Google
    </button>
  )
}
