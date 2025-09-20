"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, X, BarChart3, Users, MessageSquare, Mic, Brain } from "lucide-react"
import { useRouter, usePathname } from "next/navigation"
import { useUser } from "@/hooks/useUser"
import { canAccessDashboard } from "@/lib/permissions"

export default function MobileNavMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  const { user } = useUser()

  if (!user) return null

  const getNavigationItems = () => {
    const commonItems = [
      { 
        href: "/", 
        label: "Chat", 
        icon: MessageSquare,
        description: "AI Assistant Chat"
      },
      { 
        href: "/voice-demo", 
        label: "Voice", 
        icon: Mic,
        description: "Voice Features"
      },
    ]

    // Add dashboard navigation for users with dashboard access
    if (canAccessDashboard(user)) {
      return [
        ...commonItems,
        { 
          href: "/dashboard", 
          label: "Dashboard", 
          icon: BarChart3,
          description: "Overview & Analytics"
        },
        { 
          href: "/dashboard/students", 
          label: "Students", 
          icon: Users,
          description: "Manage Students"
        },
      ]
    }

    return commonItems
  }

  const navigationItems = getNavigationItems()

  const handleNavigate = (href) => {
    router.push(href)
    setIsOpen(false)
  }

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="md:hidden flex items-center gap-2 rounded-lg p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        aria-label="Open navigation menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Mobile Navigation Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/60 md:hidden"
              onClick={() => setIsOpen(false)}
            />
            
            {/* Navigation Menu */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 260, damping: 28 }}
              className="fixed top-0 right-0 bottom-0 z-50 w-80 bg-white dark:bg-zinc-900 border-l border-zinc-200/60 dark:border-zinc-800 md:hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-zinc-200/60 dark:border-zinc-800">
                <div className="flex items-center gap-2">
                  <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  <span className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                    MITRA
                  </span>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-lg p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  aria-label="Close navigation menu"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* User Info */}
              <div className="p-4 border-b border-zinc-200/60 dark:border-zinc-800">
                <div className="flex items-center gap-3">
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="h-10 w-10 rounded-full border-2 border-zinc-200 dark:border-zinc-700"
                  />
                  <div>
                    <div className="font-medium text-zinc-900 dark:text-zinc-100">
                      {user.name}
                    </div>
                    <div className="text-sm text-zinc-500 dark:text-zinc-400 capitalize">
                      {user.role || "Student"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Items */}
              <nav className="p-4">
                <div className="space-y-2">
                  {navigationItems.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href
                    
                    return (
                      <button
                        key={item.href}
                        onClick={() => handleNavigate(item.href)}
                        className={`
                          w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                          ${isActive 
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300" 
                            : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
                          }
                          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                        `}
                      >
                        <Icon className="h-5 w-5 shrink-0" />
                        <div className="flex flex-col items-start min-w-0">
                          <span className="font-medium">{item.label}</span>
                          <span className="text-xs opacity-75">{item.description}</span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
