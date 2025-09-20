// frontend/hooks/useMood.ts
'use client';

import { useState, useCallback } from 'react';

interface MoodData {
  mood: string;
  intensity?: number;
  notes?: string;
}

interface MoodEntry {
  mood_id: string;
  mood: string;
  intensity?: number;
  notes?: string;
  timestamp: string;
  created_at: string;
}

interface CurrentMoodResponse {
  mood_id?: string;
  mood?: string;
  intensity?: number;
  notes?: string;
  timestamp?: string;
  created_at?: string;
}

interface MoodStreamEntry {
  mood_id: string;
  student_id: string;
  student_name: string;
  mood: string;
  intensity?: number;
  timestamp: string;
}

interface MoodStreamResponse {
  mood_entries: MoodStreamEntry[];
  total_count: number;
}

interface MoodAnalyticsResponse {
  total_students: number;
  students_with_mood_sharing: number;
  total_mood_entries: number;
  recent_mood_entries_24h: number;
  mood_distribution: Record<string, number>;
  mood_percentages: Record<string, number>;
  average_moods_per_student: number;
  most_common_mood?: string;
}

export function useMood() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRequest = async <T>(
    requestFn: () => Promise<Response>
  ): Promise<T> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await requestFn();
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateMood = useCallback(
    async (studentId: string, moodData: MoodData) => {
      return handleRequest(async () => {
        return fetch(`/api/v1/students/${studentId}/mood`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(moodData),
        });
      });
    },
    []
  );

  const getCurrentMood = useCallback(
    async (studentId: string): Promise<CurrentMoodResponse> => {
      return handleRequest(async () => {
        return fetch(`/api/v1/students/${studentId}/mood`, {
          method: 'GET',
          credentials: 'include',
        });
      });
    },
    []
  );

  const getMoodStream = useCallback(
    async (limit: number = 50): Promise<MoodStreamResponse> => {
      return handleRequest(async () => {
        return fetch(`/api/v1/students/mood/stream?limit=${limit}`, {
          method: 'GET',
          credentials: 'include',
        });
      });
    },
    []
  );

  const getMoodAnalytics = useCallback(
    async (): Promise<MoodAnalyticsResponse> => {
      return handleRequest(async () => {
        return fetch('/api/v1/students/mood/analytics', {
          method: 'GET',
          credentials: 'include',
        });
      });
    },
    []
  );

  // Real-time mood updates using Server-Sent Events or polling
  const subscribeMoodUpdates = useCallback(
    (
      studentId: string,
      onMoodUpdate: (mood: CurrentMoodResponse) => void,
      pollingInterval: number = 30000 // 30 seconds
    ) => {
      let intervalId: NodeJS.Timeout;
      let isActive = true;

      const poll = async () => {
        if (!isActive) return;

        try {
          const mood = await getCurrentMood(studentId);
          if (isActive) {
            onMoodUpdate(mood);
          }
        } catch (err) {
          console.warn('Failed to poll mood updates:', err);
        }
      };

      // Initial poll
      poll();

      // Set up polling interval
      intervalId = setInterval(poll, pollingInterval);

      // Return cleanup function
      return () => {
        isActive = false;
        if (intervalId) {
          clearInterval(intervalId);
        }
      };
    },
    [getCurrentMood]
  );

  const subscribeMoodStream = useCallback(
    (
      onStreamUpdate: (stream: MoodStreamResponse) => void,
      pollingInterval: number = 60000 // 1 minute
    ) => {
      let intervalId: NodeJS.Timeout;
      let isActive = true;

      const poll = async () => {
        if (!isActive) return;

        try {
          const stream = await getMoodStream();
          if (isActive) {
            onStreamUpdate(stream);
          }
        } catch (err) {
          console.warn('Failed to poll mood stream:', err);
        }
      };

      // Initial poll
      poll();

      // Set up polling interval
      intervalId = setInterval(poll, pollingInterval);

      // Return cleanup function
      return () => {
        isActive = false;
        if (intervalId) {
          clearInterval(intervalId);
        }
      };
    },
    [getMoodStream]
  );

  return {
    updateMood,
    getCurrentMood,
    getMoodStream,
    getMoodAnalytics,
    subscribeMoodUpdates,
    subscribeMoodStream,
    isLoading,
    error,
  };
}
