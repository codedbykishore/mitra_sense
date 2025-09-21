"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/hooks/useUser";
import { canAccessDashboard } from "@/lib/permissions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Users, Brain, MessageSquare, BarChart3 } from "lucide-react";
import { StudentInfo } from "@/types/student";
import StudentListPanel from "@/components/dashboard/StudentListPanel";
import MoodSummaryPanel from "@/components/dashboard/MoodSummaryPanel";
import ConversationListPanel from "@/components/dashboard/ConversationListPanel";
import NotificationsPanel from "@/components/dashboard/NotificationsPanel";
import Breadcrumb from "@/components/Breadcrumb";
import QuickActions from "@/components/QuickActions";

export default function DashboardPage() {
  const { user, loading } = useUser();
  const router = useRouter();
  const [selectedStudent, setSelectedStudent] = useState<StudentInfo | null>(null);

  // Authentication and authorization guard
  useEffect(() => {
    if (!loading && !user) {
      router.replace("/");
    } else if (!loading && user && !canAccessDashboard(user)) {
      // Redirect users without dashboard access back to main chat
      router.replace("/");
    }
  }, [user, loading, router]);

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                MITRA Dashboard
              </h1>
              <p className="text-gray-600 mt-1">Facilitator Mental Health Monitoring</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user.role || "Facilitator"}</p>
              </div>
              <img
                src={user.picture}
                alt={user.name}
                className="h-10 w-10 rounded-full border-2 border-gray-200"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumb />
        <QuickActions />
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Student List */}
          <div className="lg:col-span-1">
            <StudentListPanel
              selectedStudent={selectedStudent}
              onStudentSelect={setSelectedStudent}
            />
            <div className="mt-6 hidden lg:block">
              <NotificationsPanel />
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Students</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">--</div>
                  <p className="text-xs text-muted-foreground">
                    Students enrolled
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Mood Entries</CardTitle>
                  <Brain className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">--</div>
                  <p className="text-xs text-muted-foreground">
                    This week
                  </p>
                </CardContent>
              </Card>

              <Card>
                <TabsTrigger value="notifications" className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Notifications
                </TabsTrigger>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Conversations</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">--</div>
                  <p className="text-xs text-muted-foreground">
                    Active chats
                  </p>
                </CardContent>
              </Card>

              <TabsContent value="notifications" className="space-y-4">
                <NotificationsPanel />
              </TabsContent>
            </div>

            {/* Tabbed Content */}
            <Card>
              <CardHeader>
                <CardTitle>
                  {selectedStudent ? `${selectedStudent.name} - Details` : "Overview"}
                </CardTitle>
                <CardDescription>
                  {selectedStudent
                    ? `View mood history and conversations for ${selectedStudent.name}`
                    : "Select a student from the list to view detailed information"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="moods" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="moods" className="flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      Mood Summary
                    </TabsTrigger>
                    <TabsTrigger value="conversations" className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      Conversations
                    </TabsTrigger>
                  </TabsList>

                  <Separator className="my-4" />

                  <TabsContent value="moods" className="space-y-4">
                    <MoodSummaryPanel selectedStudent={selectedStudent} />
                  </TabsContent>

                  <TabsContent value="conversations" className="space-y-4">
                    <ConversationListPanel selectedStudent={selectedStudent} />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
