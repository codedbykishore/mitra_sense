// components/students/MoodTracker.tsx
'use client';

import { useState } from 'react';
import { MOOD_OPTIONS, AddMoodRequest } from '@/types/student';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface MoodTrackerProps {
  studentId: string;
  studentName: string;
  onMoodAdded: () => void;
}

export function MoodTracker({ studentId, studentName, onMoodAdded }: MoodTrackerProps) {
  const [mood, setMood] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!mood) {
      setError('Please select a mood');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const requestData: AddMoodRequest = {
        mood,
        notes: notes.trim() || undefined
      };

      const response = await fetch(`/api/v1/students/${studentId}/moods`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setSuccess(`Mood "${mood}" recorded successfully!`);
        setMood('');
        setNotes('');
        onMoodAdded();
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      } else {
        throw new Error(result.message || 'Failed to record mood');
      }
    } catch (err) {
      console.error('Error adding mood:', err);
      setError(err instanceof Error ? err.message : 'Failed to record mood');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Record Mood for {studentName}
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-700 text-sm">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="mood" className="block text-sm font-medium text-gray-700 mb-2">
            Mood *
          </label>
          <Select value={mood} onValueChange={setMood}>
            <SelectTrigger>
              <SelectValue placeholder="Select a mood..." />
            </SelectTrigger>
            <SelectContent>
              {MOOD_OPTIONS.map((option) => (
                <SelectItem key={option} value={option}>
                  <span className="capitalize">{option}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <Textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any additional notes about the mood..."
            rows={3}
            maxLength={500}
            className="resize-none"
          />
          <div className="text-xs text-gray-500 mt-1">
            {notes.length}/500 characters
          </div>
        </div>

        <Button
          type="submit"
          disabled={isSubmitting || !mood}
          className="w-full"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Recording...
            </>
          ) : (
            'Record Mood'
          )}
        </Button>
      </form>
    </div>
  );
}
