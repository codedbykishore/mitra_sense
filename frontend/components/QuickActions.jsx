"use client"
import { MessageSquare, ArrowLeft, BarChart3 } from "lucide-react"
import { useRouter, usePathname } from "next/navigation"

export default function QuickActions() {
  const router = useRouter()
  const pathname = usePathname()

  const getQuickActions = () => {
    const actions = []

    // Always show chat link
    if (pathname !== "/") {
      actions.push({
        label: "Back to Chat",
        href: "/",
        icon: MessageSquare,
        variant: "primary"
      })
    }

    // Show dashboard link if not on dashboard
    if (pathname !== "/dashboard" && pathname.startsWith("/dashboard")) {
      actions.push({
        label: "Dashboard",
        href: "/dashboard",
        icon: BarChart3,
        variant: "secondary"
      })
    }

    return actions
  }

  const quickActions = getQuickActions()

  if (quickActions.length === 0) {
    return null
  }

  return (
    <div className="flex items-center gap-2 mb-6">
      {quickActions.map((action) => {
        const Icon = action.icon
        
        return (
          <button
            key={action.href}
            onClick={() => router.push(action.href)}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
              ${action.variant === "primary" 
                ? "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600" 
                : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
              }
            `}
          >
            <Icon className="h-4 w-4" />
            {action.label}
          </button>
        )
      })}
    </div>
  )
}
