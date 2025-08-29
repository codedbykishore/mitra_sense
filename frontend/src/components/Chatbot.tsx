"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  MessageSquare,
  Plus,
  Menu,
  Send,
  User,
  Bot,
  Moon,
  Sun,
  Trash2,
} from "lucide-react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  sender: "user" | "bot";
  text: string;
  markdown?: boolean;
  timestamp?: Date;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

const Chatbot: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    const saved = localStorage.getItem("chat_sessions");
    if (saved) return JSON.parse(saved);
    return [
      { id: Date.now().toString(), title: "New Chat", messages: [], createdAt: new Date() },
    ];
  });

  const [currentSessionId, setCurrentSessionId] = useState<string>(() => sessions[0].id);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentSession = sessions.find((s) => s.id === currentSessionId);

  // Persist sessions
  useEffect(() => {
    localStorage.setItem("chat_sessions", JSON.stringify(sessions));
  }, [sessions]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentSession?.messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  // Helper: update current session messages
  const updateCurrentSessionMessages = (newMessage: Message) => {
    setSessions((prev) =>
      prev.map((session) =>
        session.id === currentSessionId
          ? { ...session, messages: [...session.messages, newMessage] }
          : session
      )
    );
  };

  const createNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [],
      createdAt: new Date(),
    };
    setSessions((prev) => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    setInput("");
  };

  const updateSessionTitle = (sessionId: string, firstMessage: string) => {
    const title = firstMessage.length > 30 ? firstMessage.substring(0, 30) + "..." : firstMessage;
    setSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, title } : s))
    );
  };

  const deleteSession = (sessionId: string) => {
    if (!window.confirm("Are you sure you want to delete this chat?")) return;
    const remaining = sessions.filter((s) => s.id !== sessionId);
    setSessions(remaining);
    if (currentSessionId === sessionId) {
      remaining.length ? setCurrentSessionId(remaining[0].id) : createNewChat();
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading || !currentSession) return;

    const userMessage: Message = { sender: "user", text: input.trim(), timestamp: new Date() };
    updateCurrentSessionMessages(userMessage);

    if (currentSession.messages.length === 0) {
      updateSessionTitle(currentSessionId, input.trim());
    }

    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/v1/input/chat", {
        text: currentInput,
        context: {},
      });

      const botMessage: Message = {
        sender: "bot",
        text: res.data.response,
        markdown: res.data.markdown || false,
        timestamp: new Date(),
      };
      updateCurrentSessionMessages(botMessage);
    } catch {
      updateCurrentSessionMessages({
        sender: "bot",
        text: "⚠️ Error connecting to server. Please try again.",
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Helper: color classes based on dark mode
  const bgClass = (light: string, dark: string) => (darkMode ? dark : light);

  return (
    <div className={`flex h-screen ${bgClass("bg-white text-gray-900", "bg-gray-900 text-white")}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? "w-64" : "w-0"} transition-all duration-300 ${bgClass("bg-gray-100", "bg-gray-800")} flex flex-col overflow-hidden`}>
        <div className="p-3 border-b border-gray-500">
          <button onClick={createNewChat} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg border border-gray-500 hover:bg-gray-700 transition-colors">
            <Plus size={16} />
            <span className="text-sm">New chat</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {sessions.map((session) => (
            <div key={session.id} className={`group flex items-center justify-between p-3 mb-1 rounded-lg text-sm cursor-pointer hover:bg-gray-700 ${currentSessionId === session.id ? "bg-gray-700" : ""}`} onClick={() => setCurrentSessionId(session.id)}>
              <div className="flex items-center gap-2 truncate">
                <MessageSquare size={16} />
                <span className="truncate">{session.title}</span>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
                aria-label="Delete chat"
                className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`flex items-center justify-between px-4 py-3 border-b ${bgClass("bg-gray-100 border-gray-300", "bg-gray-800 border-gray-700")}`}>
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <Menu size={20} />
            </button>
            <h1 className="text-lg font-semibold">MITRA</h1>
          </div>
          <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700">
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {currentSession ? (
            currentSession.messages.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className={`w-16 h-16 ${bgClass("bg-gray-200", "bg-gray-700")} rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <Bot size={32} />
                  </div>
                  <h2 className="text-2xl font-semibold mb-2">How can I help you today?</h2>
                  <p className="text-gray-500">Start a conversation by typing a message below.</p>
                </div>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto px-4 py-6">
                {currentSession.messages.map((msg, idx) => (
                  <div key={idx} className={`mb-4 flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                    {msg.sender === "bot" && (
                      <div className={`w-8 h-8 rounded-full ${bgClass("bg-gray-400", "bg-gray-600")} text-white flex items-center justify-center mr-3 mt-1 flex-shrink-0`}>
                        <Bot size={16} />
                      </div>
                    )}
                    <div className={`max-w-[85%] sm:max-w-[72%] px-4 py-2 rounded-2xl whitespace-pre-wrap leading-relaxed ${msg.sender === "user" ? bgClass("bg-gray-300 text-gray-900 rounded-br-md", "bg-gray-600 text-white rounded-br-md") : bgClass("bg-gray-100 text-gray-900 rounded-bl-md", "bg-gray-700 text-white rounded-bl-md")}`}>
                      {msg.markdown ? (
                        <>
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                          <button onClick={() => { navigator.clipboard.writeText(msg.text); alert("Copied!"); }} className="mt-2 px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs">Copy</button>
                        </>
                      ) : msg.text}
                    </div>
                    {msg.sender === "user" && (
                      <div className={`w-8 h-8 rounded-full ${bgClass("bg-gray-400", "bg-gray-600")} text-white flex items-center justify-center ml-3 mt-1 flex-shrink-0`}>
                        <User size={16} />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="mb-6 flex justify-start">
                    <div className={`w-8 h-8 rounded-full ${bgClass("bg-gray-400", "bg-gray-600")} text-white flex items-center justify-center mr-3 mt-1`}>
                      <Bot size={16} />
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }}></div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )
          ) : (
            <div className="h-full flex items-center justify-center">
              <p>No session found. Create a new chat!</p>
            </div>
          )}
        </div>

        {/* Input */}
        <div className={`${bgClass("bg-gray-100 border-t border-gray-300", "bg-gray-800 border-t border-gray-700")} px-4 py-3`}>
          <div className="max-w-3xl mx-auto">
            <div className={`flex items-center gap-2 ${bgClass("bg-gray-200 border-gray-300", "bg-gray-700 border-gray-600")} border rounded-full px-3 py-2 focus-within:ring-2 focus-within:ring-gray-400 transition`}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Message MITRA..."
                className="flex-1 resize-none border-none outline-none text-sm bg-transparent p-2 rounded-full max-h-32 min-h-[20px]"
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className={`p-2 rounded-full ${bgClass("bg-gray-400 hover:bg-gray-500", "bg-gray-600 hover:bg-gray-500")} text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0`}
              >
                <Send size={16} />
              </button>
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">MITRA can make mistakes. Consider checking important information.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
