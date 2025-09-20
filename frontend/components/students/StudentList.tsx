// components/students/StudentList.tsx
import { StudentInfo } from '@/types/student';

interface StudentListProps {
  students: StudentInfo[];
  selectedStudent: StudentInfo | null;
  onStudentSelect: (student: StudentInfo) => void;
}

export function StudentList({ 
  students, 
  selectedStudent, 
  onStudentSelect 
}: StudentListProps) {
  if (students.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Students</h2>
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
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
              />
            </svg>
          </div>
          <p className="text-gray-600">No students found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Students ({students.length})
      </h2>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {students.map((student) => (
          <div
            key={student.user_id}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedStudent?.user_id === student.user_id
                ? 'bg-blue-50 border-2 border-blue-200'
                : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
            }`}
            onClick={() => onStudentSelect(student)}
          >
            <div className="font-medium text-gray-900">{student.name}</div>
            <div className="text-sm text-gray-600">{student.email}</div>
            {student.institution_name && (
              <div className="text-xs text-gray-500 mt-1">
                {student.institution_name}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
