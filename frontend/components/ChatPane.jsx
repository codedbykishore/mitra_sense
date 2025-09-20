"use client"

import { useState, forwardRef, useImperativeHandle, useRef, useCallback, useEffect } from "react"
import { Pencil, RefreshCw, Check, X, Square, AlertTriangle, Phone, Mic, Volume2, Heart, Menu } from "lucide-react"
import Message from "./Message"
import Composer from "./Composer"
import dynamic from 'next/dynamic'
import { useUser } from "../hooks/useUser"
import { cls } from "./utils"

// Dynamically import VoiceCompanion with no SSR to prevent hydration issues
const VoiceCompanion = dynamic(() => import("./voice/VoiceCompanion"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center p-4">
      <div className="text-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-600"></div>
        <p className="mt-2 text-sm text-zinc-600">Loading voice...</p>
      </div>
    </div>
  )
})

// Component to format AI responses with proper markdown and spacing
function FormattedResponse({ content }) {
  if (!content) return null

  // Process the content to handle markdown and proper spacing
  let processedContent = content
    // Handle bold text **text** -> <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Handle bullet points with multiple spaces *   text -> • text
    .replace(/^\*\s{2,}/gm, '• ')
    // Handle italic text *text* -> <em>text</em> (but not bullet points)
    .replace(/(?<!•\s.*)\*([^*\n]+)\*(?!\s)/g, '<em>$1</em>')

  // Smart question formatting - only for standalone questions
  processedContent = processedContent
    // Put standalone questions on new lines
    .replace(/(\. )([A-Z][^.!?]*\?\s*$)/gm, '$1\n\n$2')
    .replace(/(\. )(What|Why|When|Where|How|Do you|Can you|Have you|Are you|Is there|Could you|Would you|Will you|Should|Might)[^.!?]*\?\s*$/gm, '$1\n\n$2')

  // Clean up excessive spacing but preserve intentional paragraph breaks
  processedContent = processedContent
    .replace(/\n{3,}/g, '\n\n') // Max 2 newlines
    .trim()

  // Split into paragraphs and format
  const paragraphs = processedContent.split('\n\n').filter(p => p.trim())

  const formattedHTML = paragraphs
    .map(paragraph => {
      // Convert single newlines within paragraphs to <br/>
      const formattedParagraph = paragraph.replace(/\n/g, '<br/>')
      return `<p class="mb-3">${formattedParagraph}</p>`
    })
    .join('')

  return (
    <div className="text-sm leading-relaxed">
      <div
        dangerouslySetInnerHTML={{
          __html: formattedHTML
        }}
      />
    </div>
  )
}

function ThinkingMessage({ onPause }) {
  return (
    <Message role="assistant">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]"></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]"></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400"></div>
        </div>
        <span className="text-sm text-zinc-500">AI is thinking...</span>
        <button
          onClick={onPause}
          className="ml-auto inline-flex items-center gap-1 rounded-full border border-zinc-300 px-2 py-1 text-xs text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800"
        >
          <Square className="h-3 w-3" /> Pause
        </button>
      </div>
    </Message>
  )
}

const ChatPane = forwardRef(function ChatPane(
  { conversation, onSend, onEditMessage, onResendMessage, onLoadMore, isThinking, onPauseThinking, loadingHistory, historyError, setSidebarOpen, sidebarCollapsed },
  ref,
) {
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [isVoiceMode, setIsVoiceMode] = useState(false)
  const [crisisAlert, setCrisisAlert] = useState(null)
  const [voiceError, setVoiceError] = useState(null)
  const composerRef = useRef(null)
  const voiceAnnouncementRef = useRef(null)
  const { user } = useUser()

  // Cleanup voice mode on unmount
  useEffect(() => {
    return () => {
      // Reset voice mode and clear any pending states when component unmounts
      setIsVoiceMode(false)
      setCrisisAlert(null)
      setVoiceError(null)
    }
  }, [])

  // Get user's auth token (in real implementation, this would come from authentication)
  const userAuthToken = user?.authToken || 'demo-token'

  // User's cultural preferences (could come from user profile)
  const userCulturalPreferences = {
    language: user?.preferredLanguage || 'en-US',
    familyContext: user?.familyContext || 'individual',
    greetingStyle: user?.greetingStyle || 'informal',
  }

  // Handle voice mode toggle
  const handleVoiceModeToggle = useCallback(() => {
    setIsVoiceMode(prev => {
      const newVoiceMode = !prev

      // Clear any existing errors when toggling voice mode
      if (newVoiceMode) {
        setVoiceError(null)
        // Announce voice mode activation for screen readers
        announceToScreenReader('Voice mode activated. You can now record voice messages.')
      } else {
        // Announce voice mode deactivation
        announceToScreenReader('Voice mode deactivated. Switched back to text input.')
      }

      return newVoiceMode
    })
  }, [])

  // Announce messages to screen readers
  const announceToScreenReader = useCallback((message) => {
    if (voiceAnnouncementRef.current) {
      voiceAnnouncementRef.current.textContent = message
      // Clear after announcement
      setTimeout(() => {
        if (voiceAnnouncementRef.current) {
          voiceAnnouncementRef.current.textContent = ''
        }
      }, 1000)
    }
  }, [])

  // Handle voice errors (microphone, network, playback issues)
  const handleVoiceError = useCallback((errorType, message) => {
    console.error('Voice error:', { errorType, message })

    setVoiceError({
      type: errorType,
      message,
      timestamp: new Date(),
    })

    // Announce error to screen readers
    announceToScreenReader(`Voice error: ${message}`)

    // Auto-clear error after 10 seconds
    setTimeout(() => {
      setVoiceError(null)
    }, 10000)

    // For critical errors, switch back to text mode
    if (errorType === 'microphone-permission' || errorType === 'network-error') {
      setIsVoiceMode(false)
      announceToScreenReader('Switched back to text input due to voice error.')
    }
  }, [announceToScreenReader])

  // Handle emergency/crisis detection from voice companion
  const handleEmergency = useCallback((crisisScore, suggestedActions) => {
    console.log('🚨 Crisis detected:', { crisisScore, suggestedActions })

    // Set crisis alert for UI display
    setCrisisAlert({
      score: crisisScore,
      actions: suggestedActions,
      timestamp: new Date(),
    })

    // Announce crisis to screen readers
    announceToScreenReader(`Crisis level detected. Crisis score: ${Math.round(crisisScore * 100)}%. Immediate support is available.`)

    // Auto-clear crisis alert after 30 seconds unless user acknowledges
    setTimeout(() => {
      setCrisisAlert(null)
    }, 30000)

    // In a real implementation, this would:
    // - Log the crisis incident
    // - Notify emergency contacts
    // - Show crisis support resources
    // - Potentially escalate to mental health professionals
  }, [announceToScreenReader])

  // Add voice interaction to chat history
  const addToChatHistory = useCallback((transcription, response, emotion) => {
    console.log('Voice interaction completed:', { transcription, response, emotion })

    // Announce completion to screen readers
    announceToScreenReader(`Voice interaction completed. Message transcribed and response received.`)

    // Create voice interaction messages for chat history
    const userMessage = {
      id: `voice-user-${Date.now()}`,
      role: 'user',
      content: transcription,
      type: 'voice',
      emotion: emotion?.primaryEmotion,
      timestamp: new Date(),
    }

    const assistantMessage = {
      id: `voice-assistant-${Date.now()}`,
      role: 'assistant',
      content: response,
      type: 'voice',
      emotion: emotion,
      timestamp: new Date(),
    }

    // Add both messages to conversation
    // Note: This is a simplified implementation
    // In a real app, this would properly update the conversation state
    if (conversation && conversation.messages) {
      conversation.messages.push(userMessage, assistantMessage)
    }

    // Auto-switch back to text mode after voice interaction
    setIsVoiceMode(false)
    announceToScreenReader('Voice interaction completed. Switched back to text mode.')
  }, [conversation, announceToScreenReader])

  useImperativeHandle(
    ref,
    () => ({
      insertTemplate: (templateContent) => {
        composerRef.current?.insertTemplate(templateContent)
      },
    }),
    [],
  )

  if (!conversation) return null

  const messages = Array.isArray(conversation.messages) ? conversation.messages : []
  const count = messages.length || conversation.messageCount || 0

  function startEdit(m) {
    setEditingId(m.id)
    setDraft(m.content)
  }
  function cancelEdit() {
    setEditingId(null)
    setDraft("")
  }
  function saveEdit() {
    if (!editingId) return
    onEditMessage?.(editingId, draft)
    cancelEdit()
  }
  function saveAndResend() {
    if (!editingId) return
    onEditMessage?.(editingId, draft)
    onResendMessage?.(editingId)
    cancelEdit()
  }

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col">
      {/* Screen reader announcements */}
      <div
        ref={voiceAnnouncementRef}
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />

      {/* Mobile Menu Button - Only visible on small screens when sidebar is collapsed */}
      {setSidebarOpen && sidebarCollapsed && (
        <div className="md:hidden fixed top-4 left-4 z-30">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-xl p-3 bg-white shadow-lg border border-zinc-200 hover:bg-zinc-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:bg-zinc-900 dark:border-zinc-800 dark:hover:bg-zinc-800"
            aria-label="Open navigation menu"
          >
            <Menu className="h-5 w-5 text-zinc-700 dark:text-zinc-300" />
          </button>
        </div>
      )}

      <div className="h-4"></div>

      {/* Crisis Alert Banner */}
      {crisisAlert && (
        <div
          className="mx-4 mb-4 rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Crisis Level Detected ({Math.round(crisisAlert.score * 100)}%)
              </h3>
              <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                Immediate support is available. You are not alone.
              </p>
              {crisisAlert.actions.length > 0 && (
                <ul className="mt-2 text-xs text-red-600 dark:text-red-400" aria-label="Suggested actions">
                  {crisisAlert.actions.map((action, index) => (
                    <li key={index}>• {action}</li>
                  ))}
                </ul>
              )}
              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={() => window.open('tel:14416')}
                  className="inline-flex items-center gap-1 rounded bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                  aria-label="Call Tele MANAS crisis helpline"
                >
                  <Phone className="h-3 w-3" aria-hidden="true" />
                  Call Tele MANAS (14416)
                </button>
                <button
                  onClick={() => setCrisisAlert(null)}
                  className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                  aria-label="Acknowledge crisis alert"
                >
                  Acknowledge
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Error Display */}
      {voiceError && (
        <div
          className="mx-4 mb-4 rounded-lg border border-yellow-200 bg-yellow-50 p-4 shadow-sm dark:border-yellow-800 dark:bg-yellow-900/20"
          role="alert"
          aria-live="polite"
        >
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5 mr-3 flex-shrink-0" aria-hidden="true" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Voice Error: {voiceError.type}
              </h3>
              <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
                {voiceError.message}
              </p>
              {voiceError.type === 'microphone-permission' && (
                <p className="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
                  Please allow microphone access in your browser settings and try again.
                </p>
              )}
              {voiceError.type === 'network-error' && (
                <p className="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
                  Check your internet connection and try again.
                </p>
              )}
              <div className="mt-2">
                <button
                  onClick={() => setVoiceError(null)}
                  className="text-xs text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-200 focus:outline-none focus:underline"
                  aria-label="Dismiss voice error"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Companion Integration */}
      {isVoiceMode && (
        <div
          className="mx-4 mb-4 rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20"
          role="region"
          aria-label="Voice interaction interface"
        >
          <div className="p-2 border-b border-blue-200 dark:border-blue-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mic className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Voice Mode Active
                </span>
              </div>
              <button
                onClick={() => setIsVoiceMode(false)}
                className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                aria-label="Exit voice mode"
              >
                Exit Voice Mode
              </button>
            </div>
          </div>
          <VoiceCompanion
            authToken={userAuthToken}
            culturalContext={userCulturalPreferences}
            chatPaneMode={true}
            crisisThreshold={0.7}
            onCrisisDetected={handleEmergency}
            onInteractionComplete={addToChatHistory}
            onError={handleVoiceError}
            showAdvancedControls={false}
            className="voice-chat-integration"
          />
        </div>
      )}

      <div className="flex-1 space-y-5 overflow-y-auto px-4 py-6 sm:px-8">
        {/* Chat History Error Display */}
        {historyError && (
          <div
            className="mx-auto mb-4 max-w-md rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20"
            role="alert"
            aria-live="polite"
          >
            <div className="flex items-start">
              <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" aria-hidden="true" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Chat History Error
                </h3>
                <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                  {historyError}
                </p>
                <div className="mt-2">
                  <button
                    onClick={() => window.location.reload()}
                    className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 focus:outline-none focus:underline"
                    aria-label="Refresh page to retry loading chat history"
                  >
                    Refresh Page
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat History Loading Indicator */}
        {loadingHistory && (
          <div className="mx-auto mb-4 max-w-md text-center">
            <div className="flex items-center justify-center gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-300 border-t-blue-600" />
              <span className="text-sm text-blue-800 dark:text-blue-200">
                Loading chat history...
              </span>
            </div>
          </div>
        )}

        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-2xl font-bold">
              M
            </div>
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">Chat with Mitra</h2>
              <p className="text-lg text-zinc-600 dark:text-zinc-400">No messages yet. Say hello to start.</p>
              <div className="space-y-2 text-sm text-zinc-500 dark:text-zinc-400 max-w-md">
                <p className="italic">"You're never alone when you have someone to talk to."</p>
                <p className="italic">"Every conversation is a new beginning."</p>
                <p className="italic">"I'm here to listen and help whenever you need."</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Load More Button */}
            {conversation?.hasMore && messages.length > 0 && (
              <div className="text-center mb-6">
                <button
                  onClick={onLoadMore}
                  disabled={loadingHistory}
                  className={`
                    inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition-colors
                    ${loadingHistory 
                      ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed dark:border-gray-700 dark:bg-gray-800 dark:text-gray-600'
                      : 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-blue-700 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40'
                    }
                  `}
                  aria-label="Load more messages from chat history"
                >
                  {loadingHistory ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
                      Loading...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4" />
                      Load More Messages
                    </>
                  )}
                </button>
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id} className="space-y-2">
                {editingId === m.id ? (
                  <div className={cls("rounded-2xl border p-2", "border-zinc-200 dark:border-zinc-800")}>
                    <textarea
                      value={draft}
                      onChange={(e) => setDraft(e.target.value)}
                      className="w-full resize-y rounded-xl bg-transparent p-2 text-sm outline-none"
                      rows={3}
                    />
                    <div className="mt-2 flex items-center gap-2">
                      <button
                        onClick={saveEdit}
                        className="inline-flex items-center gap-1 rounded-full bg-zinc-900 px-3 py-1.5 text-xs text-white dark:bg-white dark:text-zinc-900"
                      >
                        <Check className="h-3.5 w-3.5" /> Save
                      </button>
                      <button
                        onClick={saveAndResend}
                        className="inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs"
                      >
                        <RefreshCw className="h-3.5 w-3.5" /> Save & Resend
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs"
                      >
                        <X className="h-3.5 w-3.5" /> Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <Message role={m.role}>
                    <div className="whitespace-pre-wrap">
                      {m.role === 'assistant' ? (
                        <FormattedResponse content={m.content} />
                      ) : (
                        m.content
                      )}
                    </div>

                    {/* Voice interaction indicators */}
                    {m.type === 'voice' && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                        {m.role === 'user' ? (
                          <div className="flex items-center gap-1">
                            <Mic className="h-3 w-3" />
                            <span>Voice message</span>
                            {m.emotion && (
                              <span className="ml-2 rounded px-1.5 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                                {m.emotion}
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center gap-1">
                            <Volume2 className="h-3 w-3" />
                            <span>Voice response</span>
                            {m.emotion && (
                              <div className="ml-2 flex items-center gap-1">
                                <Heart className="h-3 w-3" />
                                <span className="rounded px-1.5 py-0.5 bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300">
                                  {m.emotion.primaryEmotion} ({Math.round(m.emotion.confidence * 100)}%)
                                </span>
                                {m.emotion.stressLevel >= 0.7 && (
                                  <span className="rounded px-1.5 py-0.5 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">
                                    High stress
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {m.role === "user" && (
                      <div className="mt-1 flex gap-2 text-[11px] text-zinc-500">
                        <button className="inline-flex items-center gap-1 hover:underline" onClick={() => startEdit(m)}>
                          <Pencil className="h-3.5 w-3.5" /> Edit
                        </button>
                        <button
                          className="inline-flex items-center gap-1 hover:underline"
                          onClick={() => onResendMessage?.(m.id)}
                        >
                          <RefreshCw className="h-3.5 w-3.5" /> Resend
                        </button>
                      </div>
                    )}
                  </Message>
                )}
              </div>
            ))}
            {isThinking && <ThinkingMessage onPause={onPauseThinking} />}
          </>
        )}
      </div>

      <Composer
        ref={composerRef}
        onSend={async (text) => {
          if (!text.trim()) return
          setBusy(true)
          await onSend?.(text)
          setBusy(false)
        }}
        busy={busy}
        onVoiceModeToggle={handleVoiceModeToggle}
        isVoiceMode={isVoiceMode}
      />
    </div>
  )
})

export default ChatPane
