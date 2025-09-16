"use client"
import { useState, useEffect } from "react"
import { User, Globe, HelpCircle, Crown, BookOpen, ChevronRight } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover"
import LogoutButton from "./Logout"

export default function SettingsPopover({ children }) {
  const [open, setOpen] = useState(false)
  const [user, setUser] = useState(null)

  // Fetch current user info from backend
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("http://localhost:8000/me", {
          credentials: "include", // include session cookies
        })

        if (res.ok) {
          const data = await res.json()
          if (data.authenticated) {
            setUser({
              name: data.name,
              email: data.email,
              picture: data.picture,
              plan: data.plan,
            })
          }
        }
      } catch (err) {
        console.error("Failed to fetch user:", err)
      }
    }

    fetchUser()
  }, [])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="start" side="top">
        <div className="p-4">
          {/* User email */}
          <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">
            {user?.email || "Not logged in"}
          </div>

          {/* Profile card */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 mb-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span className="text-sm font-medium">Personal</span>
            </div>
            <div className="ml-auto">
              <div className="text-xs text-zinc-500">{user?.plan || "Free plan"}</div>
            </div>
            {user && (
              <div className="text-blue-500">
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
            )}
          </div>

          {/* Settings list */}
          <div className="space-y-1">
            <div className="text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2">Settings</div>

            <button className="flex items-center gap-3 w-full p-2 text-sm text-left hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg">
              <Globe className="h-4 w-4" />
              <span>Language</span>
              <ChevronRight className="h-4 w-4 ml-auto" />
            </button>

            <button className="flex items-center gap-3 w-full p-2 text-sm text-left hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg">
              <HelpCircle className="h-4 w-4" />
              <span>Get help</span>
            </button>

            <button className="flex items-center gap-3 w-full p-2 text-sm text-left hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg">
              <Crown className="h-4 w-4" />
              <span>Upgrade plan</span>
            </button>

            <button className="flex items-center gap-3 w-full p-2 text-sm text-left hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg">
              <BookOpen className="h-4 w-4" />
              <span>Learn more</span>
              <ChevronRight className="h-4 w-4 ml-auto" />
            </button>

            {/* Logout button component */}
            <LogoutButton />
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
