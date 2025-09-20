"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { StudentInfo, StudentsListResponse } from "@/types/student";
import { Users, UserCheck, AlertCircle } from "lucide-react";

interface StudentListPanelProps {
  selectedStudent: StudentInfo | null;
  onStudentSelect: (student: StudentInfo) => void;
}

export default function StudentListPanel({ 
  selectedStudent, 
  onStudentSelect 
}: StudentListPanelProps) {
  const [students, setStudents] = useState<StudentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch students from API
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch("/api/v1/students", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch students: ${response.statusText}`);
        }

        const data: StudentsListResponse = await response.json();
        setStudents(data.students);
      } catch (err) {
        console.error("Error fetching students:", err);
        setError(err instanceof Error ? err.message : "Failed to load students");
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  if (loading) {
    return (
      <Card className="h-fit">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Students
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-fit">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Students
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-8 text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mb-2" />
          <p className="text-sm text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-xs text-blue-600 hover:underline"
          >
            Try again
          </button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-fit">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Students
        </CardTitle>
        <CardDescription>
          {students.length} registered student{students.length !== 1 ? "s" : ""}
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        {students.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <UserCheck className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600 font-medium">No students found</p>
            <p className="text-sm text-gray-500 mt-1">
              Students will appear here once they register
            </p>
          </div>
        ) : (
          <ScrollArea className="h-[500px]">
            <div className="space-y-1 p-4">
              {students.map((student) => (
                <div
                  key={student.user_id}
                  className={`
                    p-4 rounded-lg cursor-pointer transition-all duration-200 border-2 
                    ${selectedStudent?.user_id === student.user_id
                      ? "bg-blue-50 border-blue-200 shadow-sm"
                      : "bg-white border-gray-100 hover:bg-gray-50 hover:border-gray-200"
                    }
                  `}
                  onClick={() => onStudentSelect(student)}
                >
                  <div className="flex flex-col space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {student.name}
                        </h3>
                        <p className="text-sm text-gray-600 truncate">
                          {student.email}
                        </p>
                      </div>
                      {selectedStudent?.user_id === student.user_id && (
                        <Badge variant="default" className="text-xs">
                          Selected
                        </Badge>
                      )}
                    </div>
                    
                    {student.institution_name && (
                      <div className="flex items-center gap-1">
                        <Badge variant="secondary" className="text-xs">
                          {student.institution_name}
                        </Badge>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      {student.region && (
                        <span className="flex items-center gap-1">
                          📍 {student.region}
                        </span>
                      )}
                      {student.language_preference && (
                        <span className="flex items-center gap-1">
                          🌐 {student.language_preference}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-xs text-gray-400">
                      Joined: {new Date(student.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
