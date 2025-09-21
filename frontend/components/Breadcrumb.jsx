"use client"
import { ChevronRight, Home, BarChart3, Users } from "lucide-react"
import { useRouter, usePathname } from "next/navigation"

export default function Breadcrumb() {
  const router = useRouter()
  const pathname = usePathname()

  // Generate breadcrumb items based on current path
  const getBreadcrumbItems = () => {
    const items = [
      {
        label: "Chat",
        href: "/",
        icon: Home,
        current: pathname === "/"
      }
    ]

    if (pathname.startsWith("/dashboard")) {
      items.push({
        label: "Dashboard",
        href: "/dashboard",
        icon: BarChart3,
        current: pathname === "/dashboard"
      })

      if (pathname === "/dashboard/students") {
        items.push({
          label: "Students",
          href: "/dashboard/students",
          icon: Users,
          current: true
        })
      }
    }

    if (pathname === "/voice-messaging") {
      items.push({
        label: "Voice Messaging",
        href: "/voice-messaging",
        current: true
      })
    }

    return items
  }

  const breadcrumbItems = getBreadcrumbItems()

  // Don't show breadcrumbs for single-level pages
  if (breadcrumbItems.length <= 1) {
    return null
  }

  return (
    <nav className="flex items-center space-x-1 text-sm text-zinc-600 dark:text-zinc-400 mb-6">
      {breadcrumbItems.map((item, index) => {
        const Icon = item.icon
        const isLast = index === breadcrumbItems.length - 1

        return (
          <div key={item.href} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="h-4 w-4 mx-2 text-zinc-400 dark:text-zinc-600" />
            )}
            
            {isLast ? (
              <span className="flex items-center gap-1 font-medium text-zinc-900 dark:text-zinc-100">
                {Icon && <Icon className="h-4 w-4" />}
                {item.label}
              </span>
            ) : (
              <button
                onClick={() => router.push(item.href)}
                className="flex items-center gap-1 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded px-1"
              >
                {Icon && <Icon className="h-4 w-4" />}
                {item.label}
              </button>
            )}
          </div>
        )
      })}
    </nav>
  )
}
