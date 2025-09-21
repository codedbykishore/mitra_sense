"use client"
import { motion, AnimatePresence } from "framer-motion"
import { PanelLeftClose, PanelLeftOpen, SearchIcon, Plus, Star, Clock, Settings, BarChart3, Users, MessageSquare, Mic } from "lucide-react"
import SidebarSection from "./SidebarSection"
import ConversationRow from "./ConversationRow"
import ThemeToggle from "./ThemeToggle"
import SearchModal from "./SearchModal"
import SettingsPopover from "./SettingsPopover"
import { cls } from "./utils"
import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { canAccessDashboard } from "@/lib/permissions"

// 🔹 Import global login component
import LoginButton from "./Login"

// Main Navigation Component
function MainNavSection({ user }) {
  const router = useRouter()
  const pathname = usePathname()

  const mainNavItems = [
    {
      href: "/",
      label: "Chat",
      icon: MessageSquare,
      description: "AI Assistant"
    },
    {
      href: "/voice-messaging",
      label: "Voice",
      icon: Mic,
      description: "Voice Messaging"
    }
  ]

  // Add dashboard items if user has access
  const dashboardItems = canAccessDashboard(user) ? [
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
      description: "Student Management"
    }
  ] : []

  const allNavItems = [...mainNavItems, ...dashboardItems]

  return (
    <div className="px-1">
      <div className="mb-3 px-2 text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
        Navigation
      </div>
      <div className="space-y-1">
        {allNavItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || (item.href === "/dashboard" && pathname.startsWith("/dashboard"))
          
          return (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                ${isActive 
                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300" 
                  : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
                }
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
              `}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <div className="flex flex-col items-start min-w-0">
                <span className="font-medium truncate">{item.label}</span>
                <span className="text-xs opacity-75 truncate">{item.description}</span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default function Sidebar({
  open,
  onClose,
  theme,
  setTheme,
  collapsed,
  setCollapsed,
  conversations,
  pinned,
  recent,
  selectedId,
  onSelect,
  togglePin,
  onDeleteConversation,
  onRenameConversation,
  query,
  setQuery,
  searchRef,
  createNewChat,
  sidebarCollapsed = false,
  setSidebarCollapsed = () => { },
  user = null,
}) {
  const [showSearchModal, setShowSearchModal] = useState(false)
  const [isClient, setIsClient] = useState(false)

  // Ensure component only renders animations on client side
  useEffect(() => {
    setIsClient(true)
  }, [])

  if (sidebarCollapsed) {
    return (
      <motion.aside
        initial={{ width: 320 }}
        animate={{ width: 64 }}
        transition={{ type: "spring", stiffness: 260, damping: 28 }}
        className="z-50 flex h-full shrink-0 flex-col border-r border-zinc-200/60 bg-white dark:border-zinc-800 dark:bg-zinc-900"
      >
        <div className="flex items-center justify-center border-b border-zinc-200/60 px-3 py-3 dark:border-zinc-800">
          <button
            onClick={() => setSidebarCollapsed(false)}
            className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
            aria-label="Open sidebar"
            title="Open sidebar"
          >
            <PanelLeftOpen className="h-5 w-5" />
          </button>
        </div>

        <div className="flex flex-col items-center gap-4 pt-4">
          <button
            onClick={createNewChat}
            className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
            title="New Chat"
          >
            <Plus className="h-5 w-5" />
          </button>

          <button
            onClick={() => setShowSearchModal(true)}
            className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
            title="Search"
          >
            <SearchIcon className="h-5 w-5" />
          </button>

          {/* Navigation Icons */}
          <div className="border-t border-zinc-200/60 dark:border-zinc-800 pt-4 w-full flex flex-col items-center gap-3">
            <button
              onClick={() => window.location.href = "/"}
              className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
              title="Chat"
            >
              <MessageSquare className="h-5 w-5" />
            </button>

            <button
              onClick={() => window.location.href = "/voice-messaging"}
              className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
              title="Voice Messaging"
            >
              <Mic className="h-5 w-5" />
            </button>

            {user && canAccessDashboard(user) && (
              <>
                <button
                  onClick={() => window.location.href = "/dashboard"}
                  className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
                  title="Dashboard"
                >
                  <BarChart3 className="h-5 w-5" />
                </button>

                <button
                  onClick={() => window.location.href = "/dashboard/students"}
                  className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
                  title="Students"
                >
                  <Users className="h-5 w-5" />
                </button>
              </>
            )}
          </div>

          <div className="mt-auto mb-4">
            <SettingsPopover>
              <button
                className="rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
                title="Settings"
              >
                <Settings className="h-5 w-5" />
              </button>
            </SettingsPopover>
          </div>
        </div>
      </motion.aside>
    )
  }

  return (
    <>
      <AnimatePresence>
        {open && isClient && (
          <motion.div
            key="overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/60 md:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {(open || isClient) && (
          <motion.aside
            key="sidebar"
            initial={{ x: -340 }}
            animate={{ x: open ? 0 : 0 }}
            exit={{ x: -340 }}
            transition={{ type: "spring", stiffness: 260, damping: 28 }}
            className={cls(
              "z-50 flex h-full w-80 shrink-0 flex-col border-r border-zinc-200/60 bg-white dark:border-zinc-800 dark:bg-zinc-900",
              "fixed inset-y-0 left-0 md:static md:translate-x-0",
            )}
          >
            {/* Header */}
            <div className="flex items-center gap-2 border-b border-zinc-200/60 px-3 py-3 dark:border-zinc-800">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-sm">
                  <span className="text-sm font-bold">M</span>
                </div>
                <div className="text-sm font-semibold tracking-tight">Mitra</div>
              </div>
              <div className="ml-auto flex items-center gap-1">
                <button
                  onClick={() => setSidebarCollapsed(true)}
                  className="hidden md:block rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
                  aria-label="Close sidebar"
                  title="Close sidebar"
                >
                  <PanelLeftClose className="h-5 w-5" />
                </button>

                <button
                  onClick={onClose}
                  className="md:hidden rounded-xl p-2 hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800"
                  aria-label="Close sidebar"
                >
                  <PanelLeftClose className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="px-3 pt-3">
              <div className="relative">
                <SearchIcon className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
                <input
                  id="search"
                  ref={searchRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search…"
                  onClick={() => setShowSearchModal(true)}
                  onFocus={() => setShowSearchModal(true)}
                  className="w-full rounded-full border border-zinc-200 bg-white py-2 pl-9 pr-3 text-sm outline-none placeholder:text-zinc-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-zinc-800 dark:bg-zinc-950/50"
                />
              </div>
            </div>

            {/* New Chat */}
            <div className="px-3 pt-3">
              <button
                onClick={createNewChat}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-zinc-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:bg-white dark:text-zinc-900"
              >
                <Plus className="h-4 w-4" /> Start New Chat
              </button>
            </div>

            {/* Sections */}
            <nav className="mt-4 flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-2 pb-4">
              {/* Main Navigation - All primary navigation items */}
              {user && (
                <MainNavSection user={user} />
              )}
              
              <SidebarSection
                icon={<Star className="h-4 w-4" />}
                title="PINNED CHATS"
                collapsed={collapsed.pinned}
                onToggle={() => setCollapsed((s) => ({ ...s, pinned: !s.pinned }))}
              >
                {pinned.length === 0 ? (
                  <div className="select-none rounded-lg border border-dashed border-zinc-200 px-3 py-3 text-center text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
                    Pin important threads for quick access.
                  </div>
                ) : (
                  pinned.map((c) => (
                    <ConversationRow
                      key={c.id}
                      data={c}
                      active={c.id === selectedId}
                      onSelect={() => onSelect(c.id)}
                      onTogglePin={() => togglePin(c.id)}
                      onDeleteConversation={onDeleteConversation}
                      onRenameConversation={onRenameConversation}
                    />
                  ))
                )}
              </SidebarSection>

              <SidebarSection
                icon={<Clock className="h-4 w-4" />}
                title="RECENT CHATS"
                collapsed={collapsed.recent}
                onToggle={() => setCollapsed((s) => ({ ...s, recent: !s.recent }))}
              >
                {recent.length === 0 ? (
                  <div className="select-none rounded-lg border border-dashed border-zinc-200 px-3 py-3 text-center text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
                    No conversations yet. Start a new one!
                  </div>
                ) : (
                  recent.map((c) => (
                    <ConversationRow
                      key={c.id}
                      data={c}
                      active={c.id === selectedId}
                      onSelect={() => onSelect(c.id)}
                      onTogglePin={() => togglePin(c.id)}
                      onDeleteConversation={onDeleteConversation}
                      onRenameConversation={onRenameConversation}
                      showMeta
                    />
                  ))
                )}
              </SidebarSection>
            </nav>

            {/* Footer */}
            <div className="mt-auto border-t border-zinc-200/60 px-3 py-3 dark:border-zinc-800">
              <div className="flex items-center gap-2">
                <SettingsPopover>
                  <button className="inline-flex items-center gap-2 rounded-lg px-2 py-2 text-sm hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:hover:bg-zinc-800">
                    <Settings className="h-4 w-4" /> Settings
                  </button>
                </SettingsPopover>
                <div className="ml-auto">
                  <ThemeToggle theme={theme} setTheme={setTheme} />
                </div>
              </div>

              <div className="mt-2">
                {user ? (
                  <div className="flex items-center gap-2 rounded-xl bg-zinc-50 p-2 dark:bg-zinc-800/60">
                    <div className="grid h-8 w-8 place-items-center rounded-full bg-zinc-900 text-xs font-bold text-white dark:bg-white dark:text-zinc-900">
                      {user.name?.charAt(0).toUpperCase() || "U"}
                    </div>
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{user.name}</div>
                      <div className="truncate text-xs text-zinc-500 dark:text-zinc-400">
                        {user.plan}
                      </div>
                    </div>
                  </div>
                ) : (
                  <LoginButton />
                )}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <SearchModal
        isOpen={showSearchModal}
        onClose={() => setShowSearchModal(false)}
        conversations={conversations}
        selectedId={selectedId}
        onSelect={onSelect}
        togglePin={togglePin}
        createNewChat={createNewChat}
      />
    </>
  )
}
