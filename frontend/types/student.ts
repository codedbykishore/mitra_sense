// types/student.ts
export interface StudentInfo {
  user_id: string;
  name: string;
  email: string;
  institution_name?: string;
  region?: string;
  age?: string;
  language_preference?: string;
  created_at: string;
}

export interface MoodEntry {
  mood_id: string;
  mood: string;
  notes?: string;
  created_at: string;
}

export interface StudentsListResponse {
  students: StudentInfo[];
  total_count: number;
}

export interface AddMoodRequest {
  mood: string;
  notes?: string;
}

export interface AddMoodResponse {
  success: boolean;
  message: string;
  mood_entry: MoodEntry;
}

export interface MoodsListResponse {
  student_id: string;
  moods: MoodEntry[];
  total_count: number;
}

// Common mood options for UI dropdowns
export const MOOD_OPTIONS = [
  'happy',
  'sad',
  'anxious',
  'stressed',
  'calm',
  'excited',
  'worried',
  'content',
  'frustrated',
  'hopeful',
  'tired',
  'energetic'
] as const;

export type MoodType = typeof MOOD_OPTIONS[number];
