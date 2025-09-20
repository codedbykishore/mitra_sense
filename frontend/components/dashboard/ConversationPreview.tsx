"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, Clock, User } from "lucide-react";

interface MessageInfo {
  message_id: string;
  conversation_id: string;
  sender_id: string;
  text: string;
  timestamp: string;
  metadata?: Record<string, any>;
  mood_score?: number;
}

interface ConversationInfo {
  conversation_id: string;
  participants: string[];
  created_at?: string;
  last_active_at?: string;
  participant_count: number;
}

interface ConversationPreviewProps {
  conversation: ConversationInfo;
  recentMessages: MessageInfo[];
  studentName?: string;
  showStudentBadge?: boolean;
}

export function ConversationPreview({ 
  conversation, 
  recentMessages, 
  studentName,
  showStudentBadge = false 
}: ConversationPreviewProps) {
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

  return (
    <Card className="border-l-4 border-l-blue-200 hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Conversation
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <User className="h-3 w-3" />
              {conversation.participant_count}
            </div>
            {showStudentBadge && studentName && (
              <Badge variant="secondary" className="text-xs">
                {studentName}
              </Badge>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Clock className="h-3 w-3" />
          {conversation.last_active_at 
            ? `Last active: ${formatTimestamp(conversation.last_active_at)}`
            : `Created: ${conversation.created_at ? formatTimestamp(conversation.created_at) : "Unknown"}`
          }
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {recentMessages.length > 0 ? (
          <div className="space-y-2">
            <h4 className="text-xs font-medium text-gray-700">Recent Messages:</h4>
            {recentMessages.slice(0, 2).map((message) => (
              <div key={message.message_id} className="bg-gray-50 rounded p-2">
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
                  {message.text.length > 100 
                    ? `${message.text.substring(0, 100)}...` 
                    : message.text
                  }
                </p>
              </div>
            ))}
            {recentMessages.length > 2 && (
              <p className="text-xs text-gray-500 italic">
                +{recentMessages.length - 2} more message{recentMessages.length - 2 !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500 italic">No recent messages</p>
        )}
      </CardContent>
    </Card>
  );
}
