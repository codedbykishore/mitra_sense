"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { MoodTracker } from "@/components/students/MoodTracker";
import { MoodHistory } from "@/components/students/MoodHistory";
import { StudentInfo, MoodEntry, MoodsListResponse } from "@/types/student";
import { Brain, TrendingUp, TrendingDown, Minus, AlertCircle } from "lucide-react";

interface MoodSummaryPanelProps {
  selectedStudent: StudentInfo | null;
}

interface MoodStats {
  totalEntries: number;
  recentMood: string | null;
  moodTrend: "up" | "down" | "stable";
  moodCounts: Record<string, number>;
}

const MOOD_COLORS = {
  happy: "bg-green-100 text-green-800",
  content: "bg-green-100 text-green-800",
  hopeful: "bg-green-100 text-green-800",
  excited: "bg-green-100 text-green-800",
  energetic: "bg-green-100 text-green-800",
  calm: "bg-blue-100 text-blue-800",
  sad: "bg-yellow-100 text-yellow-800",
  worried: "bg-orange-100 text-orange-800",
  anxious: "bg-red-100 text-red-800",
  stressed: "bg-red-100 text-red-800",
  frustrated: "bg-red-100 text-red-800",
  tired: "bg-gray-100 text-gray-800",
};

export default function MoodSummaryPanel({ selectedStudent }: MoodSummaryPanelProps) {
  const [moods, setMoods] = useState<MoodEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<MoodStats>({
    totalEntries: 0,
    recentMood: null,
    moodTrend: "stable",
    moodCounts: {},
  });

  const getMoodColor = (mood: string) => {
    return MOOD_COLORS[mood as keyof typeof MOOD_COLORS] || "bg-gray-100 text-gray-800";
  };

  const getTrendIcon = () => {
    switch (stats.moodTrend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  // Fetch mood data when a student is selected
  useEffect(() => {
    if (!selectedStudent) {
      setMoods([]);
      setStats({
        totalEntries: 0,
        recentMood: null,
        moodTrend: "stable",
        moodCounts: {},
      });
      return;
    }

    const fetchMoods = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `/api/v1/students/${selectedStudent.user_id}/moods?limit=20`,
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch moods: ${response.statusText}`);
        }

        const data: MoodsListResponse = await response.json();
        setMoods(data.moods);
        
        // Calculate mood statistics
        const moodCounts: Record<string, number> = {};
        data.moods.forEach((mood) => {
          moodCounts[mood.mood] = (moodCounts[mood.mood] || 0) + 1;
        });

        // Determine trend (simplified - compare first and last mood)
        let trend: "up" | "down" | "stable" = "stable";
        if (data.moods.length >= 2) {
          const positiveMoods = ["happy", "content", "hopeful", "excited", "energetic", "calm"];
          const recentMood = data.moods[0]?.mood;
          const olderMood = data.moods[data.moods.length - 1]?.mood;
          
          if (positiveMoods.includes(recentMood) && !positiveMoods.includes(olderMood)) {
            trend = "up";
          } else if (!positiveMoods.includes(recentMood) && positiveMoods.includes(olderMood)) {
            trend = "down";
          }
        }

        setStats({
          totalEntries: data.total_count,
          recentMood: data.moods[0]?.mood || null,
          moodTrend: trend,
          moodCounts,
        });
      } catch (err) {
        console.error("Error fetching moods:", err);
        setError(err instanceof Error ? err.message : "Failed to load mood data");
      } finally {
        setLoading(false);
      }
    };

    fetchMoods();
  }, [selectedStudent]);

  // Handle new mood entry
  const handleMoodAdded = (newMood: MoodEntry) => {
    setMoods(prev => [newMood, ...prev.slice(0, 19)]); // Keep latest 20
    setStats(prev => ({
      ...prev,
      totalEntries: prev.totalEntries + 1,
      recentMood: newMood.mood,
      moodCounts: {
        ...prev.moodCounts,
        [newMood.mood]: (prev.moodCounts[newMood.mood] || 0) + 1,
      },
    }));
  };

  // Fetch overall mood analytics when no student is selected
  useEffect(() => {
    if (selectedStudent) return;

    const fetchOverallMoodStats = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch("/api/v1/students/analytics/mood-summary", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch mood analytics: ${response.statusText}`);
        }

        const data = await response.json();
        
        setStats({
          totalEntries: data.total_mood_entries,
          recentMood: null,
          moodTrend: "stable",
          moodCounts: data.mood_distribution,
        });
      } catch (err) {
        console.error("Error fetching mood analytics:", err);
        setError(err instanceof Error ? err.message : "Failed to load mood analytics");
      } finally {
        setLoading(false);
      }
    };

    fetchOverallMoodStats();
  }, [selectedStudent]);

  if (!selectedStudent) {
    if (loading) {
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-8">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Overall Mood Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Total Entries
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="text-2xl font-bold">{stats.totalEntries}</div>
              <p className="text-xs text-muted-foreground">All students</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Most Common</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {Object.keys(stats.moodCounts).length > 0 ? (
                <Badge 
                  variant="secondary" 
                  className={`text-sm font-medium ${getMoodColor(
                    Object.entries(stats.moodCounts).sort(([,a], [,b]) => b - a)[0][0]
                  )}`}
                >
                  {Object.entries(stats.moodCounts).sort(([,a], [,b]) => b - a)[0][0]}
                </Badge>
              ) : (
                <span className="text-sm text-gray-500">No data</span>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Overview</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="text-sm font-medium">All Students</div>
              <p className="text-xs text-muted-foreground">Aggregated data</p>
            </CardContent>
          </Card>
        </div>

        {/* Overall Mood Distribution */}
        {Object.keys(stats.moodCounts).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Overall Mood Distribution</CardTitle>
              <CardDescription>Mood frequency across all students</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(stats.moodCounts)
                  .sort(([, a], [, b]) => b - a)
                  .map(([mood, count]) => (
                    <div key={mood} className="text-center">
                      <Badge 
                        variant="secondary" 
                        className={`w-full justify-center mb-1 ${getMoodColor(mood)}`}
                      >
                        {mood}
                      </Badge>
                      <div className="text-sm font-medium">{count}</div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}

        {Object.keys(stats.moodCounts).length === 0 && (
          <div className="text-center py-12">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">No mood data available</p>
            <p className="text-sm text-gray-500 mt-1">
              Mood entries will appear here once students start tracking their moods
            </p>
          </div>
        )}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }



  return (
    <div className="space-y-6">
      {/* Mood Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Total Entries
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">{stats.totalEntries}</div>
            <p className="text-xs text-muted-foreground">Mood records</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Recent Mood</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {stats.recentMood ? (
              <Badge 
                variant="secondary" 
                className={`text-sm font-medium ${getMoodColor(stats.recentMood)}`}
              >
                {stats.recentMood}
              </Badge>
            ) : (
              <span className="text-sm text-gray-500">No entries</span>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Mood Trend</CardTitle>
          </CardHeader>
          <CardContent className="pt-0 flex items-center gap-2">
            {getTrendIcon()}
            <span className="text-sm font-medium capitalize">
              {stats.moodTrend}
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Mood Distribution */}
      {Object.keys(stats.moodCounts).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Mood Distribution</CardTitle>
            <CardDescription>Frequency of different mood entries</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(stats.moodCounts)
                .sort(([, a], [, b]) => b - a)
                .map(([mood, count]) => (
                  <div key={mood} className="text-center">
                    <Badge 
                      variant="secondary" 
                      className={`w-full justify-center mb-1 ${getMoodColor(mood)}`}
                    >
                      {mood}
                    </Badge>
                    <div className="text-sm font-medium">{count}</div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mood Tracker */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Add New Mood Entry</CardTitle>
          <CardDescription>Record a new mood entry for {selectedStudent.name}</CardDescription>
        </CardHeader>
        <CardContent>
          <MoodTracker
            studentId={selectedStudent.user_id}
            studentName={selectedStudent.name}
            onMoodAdded={() => {
              // Refresh mood data after adding new mood
              const fetchMoods = async () => {
                try {
                  const response = await fetch(
                    `/api/v1/students/${selectedStudent.user_id}/moods?limit=20`,
                    { credentials: "include" }
                  );
                  if (response.ok) {
                    const data: MoodsListResponse = await response.json();
                    setMoods(data.moods);
                    
                    // Update stats
                    const moodCounts: Record<string, number> = {};
                    data.moods.forEach((mood) => {
                      moodCounts[mood.mood] = (moodCounts[mood.mood] || 0) + 1;
                    });

                    setStats({
                      totalEntries: data.total_count,
                      recentMood: data.moods[0]?.mood || null,
                      moodTrend: "stable", // Simplified for now
                      moodCounts,
                    });
                  }
                } catch (error) {
                  console.error("Error refreshing moods:", error);
                }
              };
              fetchMoods();
            }}
          />
        </CardContent>
      </Card>

      {/* Mood History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Mood History</CardTitle>
          <CardDescription>Latest mood entries for {selectedStudent.name}</CardDescription>
        </CardHeader>
        <CardContent>
          <MoodHistory 
            studentId={selectedStudent.user_id}
            studentName={selectedStudent.name}
            moods={moods} 
          />
        </CardContent>
      </Card>
    </div>
  );
}
