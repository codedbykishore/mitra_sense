// frontend/components/mood/MoodStream.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Heart,
  Frown,
  Smile,
  Meh,
  Angry,
  Zap,
  RefreshCw,
  Users,
} from 'lucide-react';
import { useMood } from '@/hooks/useMood';

interface MoodStreamProps {
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
  maxEntries?: number;
}

const moodOptions = [
  { value: 'happy', label: 'Happy', icon: Smile, color: 'text-green-500' },
  { value: 'sad', label: 'Sad', icon: Frown, color: 'text-blue-500' },
  { value: 'angry', label: 'Angry', icon: Angry, color: 'text-red-500' },
  { value: 'anxious', label: 'Anxious', icon: Zap, color: 'text-yellow-500' },
  { value: 'neutral', label: 'Neutral', icon: Meh, color: 'text-gray-500' },
  { value: 'excited', label: 'Excited', icon: Heart, color: 'text-pink-500' },
];

export default function MoodStream({
  autoRefresh = true,
  refreshInterval = 60000, // 1 minute
  maxEntries = 50,
}: MoodStreamProps) {
  const { getMoodStream, subscribeMoodStream, isLoading, error } = useMood();
  const [moodEntries, setMoodEntries] = useState<any[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    let cleanup: (() => void) | undefined;

    if (autoRefresh) {
      cleanup = subscribeMoodStream(
        (streamData) => {
          setMoodEntries(streamData.mood_entries);
          setLastUpdated(new Date());
        },
        refreshInterval
      );
    } else {
      // Manual refresh - load once
      const loadInitialData = async () => {
        try {
          const streamData = await getMoodStream(maxEntries);
          setMoodEntries(streamData.mood_entries);
          setLastUpdated(new Date());
        } catch (err) {
          console.error('Failed to load mood stream:', err);
        }
      };
      loadInitialData();
    }

    return cleanup;
  }, [
    autoRefresh,
    refreshInterval,
    maxEntries,
    getMoodStream,
    subscribeMoodStream,
  ]);

  const handleManualRefresh = async () => {
    try {
      const streamData = await getMoodStream(maxEntries);
      setMoodEntries(streamData.mood_entries);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to refresh mood stream:', err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInMinutes = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60)
      );

      if (diffInMinutes < 1) {
        return 'Just now';
      } else if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
      } else if (diffInMinutes < 1440) {
        const hours = Math.floor(diffInMinutes / 60);
        return `${hours}h ago`;
      } else {
        return date.toLocaleDateString();
      }
    } catch {
      return 'Unknown time';
    }
  };

  const getIntensityColor = (intensity: number) => {
    if (intensity <= 3) return 'bg-green-500';
    if (intensity <= 6) return 'bg-yellow-500';
    if (intensity <= 8) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            <CardTitle>Mood Stream</CardTitle>
            <Badge variant="secondary">{moodEntries.length}</Badge>
          </div>
          <div className="flex items-center gap-2">
            {lastUpdated && (
              <span className="text-xs text-muted-foreground">
                Updated {formatTimestamp(lastUpdated.toISOString())}
              </span>
            )}
            {!autoRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={isLoading}
              >
                <RefreshCw
                  className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`}
                />
                Refresh
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="text-sm text-red-500 mb-4">
            Error loading mood stream: {error}
          </div>
        )}

        {isLoading && moodEntries.length === 0 ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
                  <div className="flex-1 space-y-1">
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/6"></div>
                  </div>
                  <div className="h-3 bg-gray-200 rounded w-12"></div>
                </div>
              </div>
            ))}
          </div>
        ) : moodEntries.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No mood updates yet</p>
            <p className="text-sm">
              Students' moods will appear here when they share updates
            </p>
          </div>
        ) : (
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {moodEntries.map((entry) => {
                const moodOption = moodOptions.find(
                  (option) => option.value === entry.mood
                );

                return (
                  <div
                    key={`${entry.student_id}-${entry.mood_id}`}
                    className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    {moodOption && (
                      <moodOption.icon
                        className={`h-6 w-6 flex-shrink-0 ${moodOption.color}`}
                      />
                    )}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm truncate">
                          {entry.student_name}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          is feeling{' '}
                          <span className="font-medium">
                            {moodOption?.label || entry.mood}
                          </span>
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2 mt-1">
                        {entry.intensity && (
                          <Badge
                            className={`${getIntensityColor(
                              entry.intensity
                            )} text-white text-xs`}
                          >
                            {entry.intensity}/10
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {formatTimestamp(entry.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
