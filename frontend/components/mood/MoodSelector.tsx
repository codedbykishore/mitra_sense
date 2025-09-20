// frontend/components/mood/MoodSelector.tsx
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Heart, Frown, Smile, Meh, Angry, Zap } from 'lucide-react';
import { useMood } from '@/hooks/useMood';

interface MoodSelectorProps {
  studentId: string;
  onMoodUpdated?: () => void;
}

const moodOptions = [
  { value: 'happy', label: 'Happy', icon: Smile, color: 'text-green-500' },
  { value: 'sad', label: 'Sad', icon: Frown, color: 'text-blue-500' },
  { value: 'angry', label: 'Angry', icon: Angry, color: 'text-red-500' },
  { value: 'anxious', label: 'Anxious', icon: Zap, color: 'text-yellow-500' },
  { value: 'neutral', label: 'Neutral', icon: Meh, color: 'text-gray-500' },
  { value: 'excited', label: 'Excited', icon: Heart, color: 'text-pink-500' },
];

export default function MoodSelector({
  studentId,
  onMoodUpdated,
}: MoodSelectorProps) {
  const [selectedMood, setSelectedMood] = useState<string>('');
  const [intensity, setIntensity] = useState<number[]>([5]);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { updateMood } = useMood();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedMood) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await updateMood(studentId, {
        mood: selectedMood,
        intensity: intensity[0],
        notes: notes.trim() || undefined,
      });
      
      // Reset form
      setSelectedMood('');
      setIntensity([5]);
      setNotes('');
      
      // Notify parent component
      onMoodUpdated?.();
      
    } catch (error) {
      console.error('Failed to update mood:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedMoodOption = moodOptions.find(
    (option) => option.value === selectedMood
  );

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-lg">How are you feeling?</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Mood Selection */}
          <div className="space-y-2">
            <Label htmlFor="mood-select">Mood</Label>
            <Select
              value={selectedMood}
              onValueChange={setSelectedMood}
              required
            >
              <SelectTrigger id="mood-select">
                <SelectValue placeholder="Select your mood">
                  {selectedMoodOption && (
                    <div className="flex items-center gap-2">
                      <selectedMoodOption.icon
                        className={`h-4 w-4 ${selectedMoodOption.color}`}
                      />
                      <span>{selectedMoodOption.label}</span>
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {moodOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex items-center gap-2">
                      <option.icon className={`h-4 w-4 ${option.color}`} />
                      <span>{option.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Intensity Slider */}
          {selectedMood && (
            <div className="space-y-2">
              <Label htmlFor="intensity-slider">
                Intensity: {intensity[0]}/10
              </Label>
              <Slider
                id="intensity-slider"
                min={1}
                max={10}
                step={1}
                value={intensity}
                onValueChange={setIntensity}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="mood-notes">
              Notes <span className="text-muted-foreground">(optional)</span>
            </Label>
            <Textarea
              id="mood-notes"
              placeholder="What's on your mind? (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={500}
              rows={3}
            />
            {notes.length > 0 && (
              <div className="text-xs text-muted-foreground text-right">
                {notes.length}/500
              </div>
            )}
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={!selectedMood || isSubmitting}
          >
            {isSubmitting ? 'Updating...' : 'Update Mood'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
