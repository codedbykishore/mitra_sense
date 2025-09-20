// frontend/components/mood/MoodDisplay.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Heart, Frown, Smile, Meh, Angry, Zap, Clock } from 'lucide-react';
import { useMood } from '@/hooks/useMood';

interface MoodDisplayProps {
  studentId: string;
  refreshTrigger?: number; // External trigger to refresh data
}

const moodOptions = [
  { value: 'happy', label: 'Happy', icon: Smile, color: 'text-green-500' },
  { value: 'sad', label: 'Sad', icon: Frown, color: 'text-blue-500' },
  { value: 'angry', label: 'Angry', icon: Angry, color: 'text-red-500' },
  { value: 'anxious', label: 'Anxious', icon: Zap, color: 'text-yellow-500' },
  { value: 'neutral', label: 'Neutral', icon: Meh, color: 'text-gray-500' },
  { value: 'excited', label: 'Excited', icon: Heart, color: 'text-pink-500' },
];

export default function MoodDisplay({
  studentId,
  refreshTrigger,
}: MoodDisplayProps) {
  const { getCurrentMood, isLoading, error } = useMood();
  const [currentMood, setCurrentMood] = useState<any>(null);

  useEffect(() => {
    const fetchCurrentMood = async () => {
      try {
        const mood = await getCurrentMood(studentId);
        setCurrentMood(mood);
      } catch (err) {
        console.error('Failed to fetch current mood:', err);
      }
    };

    fetchCurrentMood();
  }, [studentId, getCurrentMood, refreshTrigger]);

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
        return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
      } else if (diffInMinutes < 1440) {
        const hours = Math.floor(diffInMinutes / 60);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
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

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Current Mood</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Current Mood</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Unable to load mood data
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!currentMood || !currentMood.mood) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Current Mood</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No mood recorded yet
          </p>
        </CardContent>
      </Card>
    );
  }

  const moodOption = moodOptions.find(
    (option) => option.value === currentMood.mood
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">Current Mood</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mood Display */}
        <div className="flex items-center gap-3">
          {moodOption && (
            <>
              <moodOption.icon className={`h-8 w-8 ${moodOption.color}`} />
              <div>
                <h3 className="text-xl font-semibold">{moodOption.label}</h3>
                {currentMood.intensity && (
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-muted-foreground">
                      Intensity:
                    </span>
                    <Badge
                      className={`${getIntensityColor(
                        currentMood.intensity
                      )} text-white`}
                    >
                      {currentMood.intensity}/10
                    </Badge>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Timestamp */}
        {currentMood.timestamp && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{formatTimestamp(currentMood.timestamp)}</span>
          </div>
        )}

        {/* Notes */}
        {currentMood.notes && (
          <div className="mt-3 p-3 bg-muted rounded-lg">
            <p className="text-sm italic">"{currentMood.notes}"</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
