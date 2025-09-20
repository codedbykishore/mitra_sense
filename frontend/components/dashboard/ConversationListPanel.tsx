"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { StudentInfo } from "@/types/student";
import { MessageSquare, Clock, User, AlertCircle } from "lucide-react";

interface ConversationInfo {
  conversation_id: string;
  participants: string[];
  created_at?: string;
  last_active_at?: string;
  participant_count: number;
}

interface ConversationsListResponse {
  conversations: ConversationInfo[];
  total_count: number;
}

interface MessageInfo {
  message_id: string;
  conversation_id: string;
  sender_id: string;
  text: string;
  timestamp: string;
  metadata?: Record<string, any>;
  mood_score?: number;
}

interface ConversationMessagesResponse {
  conversation_id: string;
  messages: MessageInfo[];
  message_count: number;
  limit: number;
  has_more: boolean;
}

interface ConversationPreviewProps {
  selectedStudent: StudentInfo | null;
}

interface ConversationPreview extends ConversationInfo {
  recentMessages: MessageInfo[];
  studentInvolved: boolean;
}

export default function ConversationListPanel({ selectedStudent }: ConversationPreviewProps) {
  const [conversations, setConversations] = useState<ConversationPreview[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all conversations and filter by student if selected
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all conversations for the current user (facilitator)
        const conversationsResponse = await fetch("/api/v1/conversations", {
          credentials: "include",
        });

        if (!conversationsResponse.ok) {
          throw new Error(`Failed to fetch conversations: ${conversationsResponse.statusText}`);
        }

        const conversationsData: ConversationsListResponse = await conversationsResponse.json();
        
        // Filter conversations by selected student if specified
        let filteredConversations = conversationsData.conversations;
        if (selectedStudent) {
          filteredConversations = conversationsData.conversations.filter(conv =>
            conv.participants.includes(selectedStudent.user_id)
          );
        }

        // Fetch recent messages for each conversation (limited preview)
        const conversationPreviews: ConversationPreview[] = await Promise.all(
          filteredConversations.slice(0, 10).map(async (conv) => {
            try {
              const messagesResponse = await fetch(
                `/api/v1/conversations/${conv.conversation_id}/messages?limit=3`,
                { credentials: "include" }
              );

              let recentMessages: MessageInfo[] = [];
              if (messagesResponse.ok) {
                const messagesData: ConversationMessagesResponse = await messagesResponse.json();
                recentMessages = messagesData.messages.reverse(); // Show latest messages first
              }

              return {
                ...conv,
                recentMessages,
                studentInvolved: selectedStudent ? conv.participants.includes(selectedStudent.user_id) : false,
              };
            } catch (msgError) {
              console.warn(`Failed to load messages for conversation ${conv.conversation_id}:`, msgError);
              return {
                ...conv,
                recentMessages: [],
                studentInvolved: selectedStudent ? conv.participants.includes(selectedStudent.user_id) : false,
              };
            }
          })
        );

        // Sort by last activity
        conversationPreviews.sort((a, b) => {
          const aTime = a.last_active_at || a.created_at || "0";
          const bTime = b.last_active_at || b.created_at || "0";
          return new Date(bTime).getTime() - new Date(aTime).getTime();
        });

        setConversations(conversationPreviews);
      } catch (err) {
        console.error("Error fetching conversations:", err);
        setError(err instanceof Error ? err.message : "Failed to load conversations");
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, [selectedStudent]);

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffHours = diffMs / (1000 * 60 * 60);
      const diffDays = diffMs / (1000 * 60 * 60 * 24);

      if (diffHours < 1) {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return `${diffMins}m ago`;
      } else if (diffHours < 24) {
        return `${Math.floor(diffHours)}h ago`;
      } else if (diffDays < 7) {
        return `${Math.floor(diffDays)}d ago`;
      } else {
        return date.toLocaleDateString();
      }
    } catch {
      return timestamp;
    }
  };

  const getMoodColor = (moodScore?: number) => {
    if (!moodScore) return "bg-gray-100 text-gray-800";
    
    if (moodScore >= 0.7) return "bg-green-100 text-green-800";
    if (moodScore >= 0.4) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getMoodLabel = (moodScore?: number) => {
    if (!moodScore) return "Neutral";
    
    if (moodScore >= 0.7) return "Positive";
    if (moodScore >= 0.4) return "Neutral";
    return "Concerning";
  };

  if (!selectedStudent && conversations.length === 0 && !loading) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 font-medium">No student selected</p>
        <p className="text-sm text-gray-500 mt-1">
          Select a student to view their conversations, or view all conversations
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
        <p className="text-sm text-red-600">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-2 text-xs text-blue-600 hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 font-medium">
          {selectedStudent ? `No conversations found for ${selectedStudent.name}` : "No conversations found"}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Conversations will appear here once students start chatting
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Conversation Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Total Conversations
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">{conversations.length}</div>
            <p className="text-xs text-muted-foreground">
              {selectedStudent ? `For ${selectedStudent.name}` : "All conversations"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-sm font-medium">
              {conversations[0]?.last_active_at 
                ? formatTimestamp(conversations[0].last_active_at)
                : "No recent activity"
              }
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Average Participants</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">
              {conversations.length > 0 
                ? Math.round(conversations.reduce((sum, conv) => sum + conv.participant_count, 0) / conversations.length)
                : 0
              }
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Conversations List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {selectedStudent ? `Conversations with ${selectedStudent.name}` : "Recent Conversations"}
          </CardTitle>
          <CardDescription>
            {conversations.length} conversation{conversations.length !== 1 ? "s" : ""} found
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[400px]">
            <div className="space-y-4 p-4">
              {conversations.map((conversation) => (
                <Card key={conversation.conversation_id} className="border-l-4 border-l-blue-200">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Conversation
                      </CardTitle>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <User className="h-3 w-3" />
                        {conversation.participant_count} participant{conversation.participant_count !== 1 ? "s" : ""}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      {conversation.last_active_at 
                        ? `Last active: ${formatTimestamp(conversation.last_active_at)}`
                        : `Created: ${conversation.created_at ? formatTimestamp(conversation.created_at) : "Unknown"}`
                      }
                      {selectedStudent && conversation.studentInvolved && (
                        <Badge variant="secondary" className="text-xs">
                          {selectedStudent.name} involved
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    {conversation.recentMessages.length > 0 ? (
                      <div className="space-y-2">
                        <h4 className="text-xs font-medium text-gray-700">Recent Messages:</h4>
                        {conversation.recentMessages.map((message) => (
                          <div key={message.message_id} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs text-gray-500">
                                {formatTimestamp(message.timestamp)}
                              </span>
                              {message.mood_score && (
                                <Badge 
                                  variant="secondary" 
                                  className={`text-xs ${getMoodColor(message.mood_score)}`}
                                >
                                  {getMoodLabel(message.mood_score)}
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-700 line-clamp-2">
                              {message.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No messages available</p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
