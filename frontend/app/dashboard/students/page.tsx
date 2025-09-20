'use client';

import { useState, useEffect } from 'react';
import { StudentInfo, MoodEntry } from '@/types/student';
import { StudentList } from '@/components/students/StudentList';
import { MoodTracker } from '@/components/students/MoodTracker';
import { MoodHistory } from '@/components/students/MoodHistory';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import Breadcrumb from '@/components/Breadcrumb';
import QuickActions from '@/components/QuickActions';

export default function StudentsPage() {
  const [students, setStudents] = useState<StudentInfo[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<StudentInfo | null>(null);
  const [moods, setMoods] = useState<MoodEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch students list
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/students');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch students: ${response.statusText}`);
        }
        
        const data = await response.json();
        setStudents(data.students || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching students:', err);
        setError(err instanceof Error ? err.message : 'Failed to load students');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  // Fetch moods for selected student
  useEffect(() => {
    const fetchMoods = async () => {
      if (!selectedStudent) {
        setMoods([]);
        return;
      }

      try {
        const response = await fetch(
          `/api/v1/students/${selectedStudent.user_id}/moods?limit=20`
        );
        
        if (!response.ok) {
          throw new Error(`Failed to fetch moods: ${response.statusText}`);
        }
        
        const data = await response.json();
        setMoods(data.moods || []);
      } catch (err) {
        console.error('Error fetching moods:', err);
        setError(err instanceof Error ? err.message : 'Failed to load moods');
      }
    };

    fetchMoods();
  }, [selectedStudent, refreshTrigger]);

  const handleStudentSelect = (student: StudentInfo) => {
    setSelectedStudent(student);
    setError(null);
  };

  const handleMoodAdded = () => {
    // Trigger a refresh of mood data
    setRefreshTrigger(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Breadcrumb />
      <QuickActions />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Student Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor student well-being and mood tracking
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 font-medium">Error</p>
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Students List */}
        <div className="lg:col-span-1">
          <StudentList
            students={students}
            selectedStudent={selectedStudent}
            onStudentSelect={handleStudentSelect}
          />
        </div>

        {/* Student Details and Mood Tracking */}
        <div className="lg:col-span-2 space-y-6">
          {selectedStudent ? (
            <>
              {/* Student Info Card */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  {selectedStudent.name}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Email:</span>
                    <span className="ml-2 text-gray-600">{selectedStudent.email}</span>
                  </div>
                  {selectedStudent.institution_name && (
                    <div>
                      <span className="font-medium text-gray-700">Institution:</span>
                      <span className="ml-2 text-gray-600">
                        {selectedStudent.institution_name}
                      </span>
                    </div>
                  )}
                  {selectedStudent.region && (
                    <div>
                      <span className="font-medium text-gray-700">Region:</span>
                      <span className="ml-2 text-gray-600">{selectedStudent.region}</span>
                    </div>
                  )}
                  {selectedStudent.age && (
                    <div>
                      <span className="font-medium text-gray-700">Age:</span>
                      <span className="ml-2 text-gray-600">{selectedStudent.age}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Mood Tracker */}
              <MoodTracker
                studentId={selectedStudent.user_id}
                studentName={selectedStudent.name}
                onMoodAdded={handleMoodAdded}
              />

              {/* Mood History */}
              <MoodHistory
                studentId={selectedStudent.user_id}
                studentName={selectedStudent.name}
                moods={moods}
              />
            </>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
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
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select a Student
              </h3>
              <p className="text-gray-600">
                Choose a student from the list to view their mood history and add new entries.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
