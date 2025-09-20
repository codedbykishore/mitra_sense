// components/students/MoodHistory.tsx
import { MoodEntry } from '@/types/student';

interface MoodHistoryProps {
  studentId: string;
  studentName: string;
  moods: MoodEntry[];
}

// Helper function to get mood emoji
const getMoodEmoji = (mood: string): string => {
  const moodEmojis: Record<string, string> = {
    happy: '😊',
    sad: '😢',
    anxious: '😰',
    stressed: '😫',
    calm: '😌',
    excited: '🤩',
    worried: '😟',
    content: '😊',
    frustrated: '😤',
    hopeful: '🤗',
    tired: '😴',
    energetic: '⚡'
  };
  return moodEmojis[mood.toLowerCase()] || '😐';
};

// Helper function to get mood color
const getMoodColor = (mood: string): string => {
  const moodColors: Record<string, string> = {
    happy: 'bg-green-100 text-green-800 border-green-200',
    sad: 'bg-blue-100 text-blue-800 border-blue-200',
    anxious: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    stressed: 'bg-red-100 text-red-800 border-red-200',
    calm: 'bg-indigo-100 text-indigo-800 border-indigo-200',
    excited: 'bg-orange-100 text-orange-800 border-orange-200',
    worried: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    content: 'bg-green-100 text-green-800 border-green-200',
    frustrated: 'bg-red-100 text-red-800 border-red-200',
    hopeful: 'bg-teal-100 text-teal-800 border-teal-200',
    tired: 'bg-gray-100 text-gray-800 border-gray-200',
    energetic: 'bg-purple-100 text-purple-800 border-purple-200'
  };
  return moodColors[mood.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-200';
};

// Helper function to format date
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
};

export function MoodHistory({ studentId, studentName, moods }: MoodHistoryProps) {
  if (moods.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Mood History for {studentName}
        </h3>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <svg
              className="mx-auto h-12 w-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p className="text-gray-600">No mood entries recorded yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Mood History for {studentName} ({moods.length} entries)
      </h3>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {moods.map((mood) => (
          <div
            key={mood.mood_id}
            className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg"
          >
            {/* Mood Icon */}
            <div className="text-2xl flex-shrink-0">
              {getMoodEmoji(mood.mood)}
            </div>

            {/* Mood Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium border ${getMoodColor(mood.mood)}`}
                >
                  {mood.mood.charAt(0).toUpperCase() + mood.mood.slice(1)}
                </span>
                <span className="text-xs text-gray-500">
                  {formatDate(mood.created_at)}
                </span>
              </div>

              {mood.notes && (
                <p className="text-sm text-gray-700 leading-relaxed">
                  {mood.notes}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Mood Summary */}
      {moods.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Mood Summary</h4>
          <div className="flex flex-wrap gap-2">
            {Array.from(new Set(moods.slice(0, 10).map(m => m.mood))).map(uniqueMood => {
              const count = moods.slice(0, 10).filter(m => m.mood === uniqueMood).length;
              return (
                <span
                  key={uniqueMood}
                  className={`px-2 py-1 rounded-full text-xs font-medium border ${getMoodColor(uniqueMood)}`}
                >
                  {getMoodEmoji(uniqueMood)} {uniqueMood} ({count})
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
