"use client"

import { useState, useRef, useEffect } from "react"
import { Star, MoreHorizontal, Trash2, Edit3 } from "lucide-react"
import { cls, timeAgo } from "./utils"
import { motion, AnimatePresence } from "framer-motion"

export default function ConversationRow({
  data,
  active,
  onSelect,
  onTogglePin,
  onDeleteConversation,
  onRenameConversation,
  showMeta,
}) {
  const [showMenu, setShowMenu] = useState(false)
  const [isRenaming, setIsRenaming] = useState(false)
  const [newTitle, setNewTitle] = useState(data.title)
  const menuRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false)
      }
    }

    if (showMenu) {
      document.addEventListener("mousedown", handleClickOutside)
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [showMenu])

  useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isRenaming])

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete "${data.title}"?`)) {
      onDeleteConversation?.(data.id)
    }
    setShowMenu(false)
  }

  const handleRename = () => {
    setIsRenaming(true)
    setShowMenu(false)
  }

  const handleRenameSubmit = () => {
    if (newTitle.trim() && newTitle.trim() !== data.title) {
      onRenameConversation?.(data.id, newTitle.trim())
    }
    setIsRenaming(false)
    setNewTitle(data.title)
  }

  const handleRenameCancel = () => {
    setIsRenaming(false)
    setNewTitle(data.title)
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleRenameSubmit()
    } else if (e.key === "Escape") {
      handleRenameCancel()
    }
  }

  const count = Array.isArray(data.messages) ? data.messages.length : data.messageCount

  return (
    <div className="group relative">
      <button
        onClick={onSelect}
        className={cls(
          "-mx-1 flex w-[calc(100%+8px)] items-center gap-2 rounded-lg px-2 py-2 text-left",
          active
            ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800/60 dark:text-zinc-100"
            : "hover:bg-zinc-100 dark:hover:bg-zinc-800",
        )}
        title={data.title}
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            {isRenaming ? (
              <input
                ref={inputRef}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onBlur={handleRenameSubmit}
                onKeyDown={handleKeyDown}
                className="truncate text-sm font-medium tracking-tight bg-transparent border-none outline-none min-w-0 flex-1"
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <span className="truncate text-sm font-medium tracking-tight">{data.title}</span>
            )}
            <span className="shrink-0 text-[11px] text-zinc-500 dark:text-zinc-400">{timeAgo(data.updatedAt)}</span>
          </div>
          {showMeta && <div className="mt-0.5 text-[11px] text-zinc-500 dark:text-zinc-400">{count} messages</div>}
        </div>

        <div className="flex items-center gap-1">
          {/* Pin as a div to avoid nested button */}
          <div
            onClick={(e) => {
              e.stopPropagation()
              onTogglePin()
            }}
            role="button"
            title={data.pinned ? "Unpin" : "Pin"}
            className="rounded-md p-1 text-zinc-500 opacity-0 transition group-hover:opacity-100 hover:bg-zinc-200/50 dark:text-zinc-300 dark:hover:bg-zinc-700/60"
          >
            {data.pinned ? (
              <Star className="h-4 w-4 fill-zinc-800 text-zinc-800 dark:fill-zinc-200 dark:text-zinc-200" />
            ) : (
              <Star className="h-4 w-4" />
            )}
          </div>

          {/* Menu */}
          <div className="relative" ref={menuRef}>
            <div
              onClick={(e) => {
                e.stopPropagation()
                setShowMenu(!showMenu)
              }}
              role="button"
              className="rounded-md p-1 text-zinc-500 opacity-0 transition group-hover:opacity-100 hover:bg-zinc-200/50 dark:text-zinc-300 dark:hover:bg-zinc-700/60"
              aria-label="More options"
            >
              <MoreHorizontal className="h-3 w-3" />
            </div>

            <AnimatePresence>
              {showMenu && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="absolute right-0 top-full mt-1 w-32 rounded-lg border border-zinc-200 bg-white py-1 shadow-lg dark:border-zinc-800 dark:bg-zinc-900 z-[100]"
                >
                  <div
                    onClick={(e) => {
                      e.stopPropagation()
                      handleRename()
                    }}
                    role="button"
                    className="w-full px-3 py-1.5 text-left text-xs text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 flex items-center gap-2"
                  >
                    <Edit3 className="h-3 w-3" />
                    Rename
                  </div>
                  <div
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete()
                    }}
                    role="button"
                    className="w-full px-3 py-1.5 text-left text-xs text-red-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 flex items-center gap-2"
                  >
                    <Trash2 className="h-3 w-3" />
                    Delete
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </button>
    </div>
  )
}
