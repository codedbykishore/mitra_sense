/**
 * Example Student Dashboard Integration for Feature 5
 * Shows how to integrate Privacy Settings and Access Logs into existing dashboard
 */

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { MoodHistory } from './MoodHistory';
import { PrivacyTab } from './PrivacyTab';
import { User, Activity, Shield, History } from 'lucide-react';

interface StudentDashboardProps {
  studentId: string;
  currentUser: {
    id: string;
    role: string;
    name: string;
  };
  studentInfo: {
    name: string;
    email: string;
    institution?: string;
  };
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({
  studentId,
  currentUser,
  studentInfo
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  const isOwnProfile = currentUser.id === studentId;
  const isInstitutionAdmin = currentUser.role === 'institution';

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {isOwnProfile ? 'My Dashboard' : `${studentInfo.name}'s Profile`}
        </h1>
        <p className="text-gray-600 mt-2">
          {studentInfo.email} {studentInfo.institution && `• ${studentInfo.institution}`}
        </p>
      </div>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="moods" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Mood History
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Privacy
          </TabsTrigger>
          <TabsTrigger 
            value="logs" 
            className="flex items-center gap-2"
            disabled={!isInstitutionAdmin}
          >
            <History className="h-4 w-4" />
            Access Logs
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Student Information Card */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <h3 className="font-semibold text-lg mb-4">Student Information</h3>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-600">Name:</span>
                  <p className="font-medium">{studentInfo.name}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Email:</span>
                  <p className="font-medium">{studentInfo.email}</p>
                </div>
                {studentInfo.institution && (
                  <div>
                    <span className="text-sm text-gray-600">Institution:</span>
                    <p className="font-medium">{studentInfo.institution}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Stats Card */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <h3 className="font-semibold text-lg mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Conversations</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Mood Entries</span>
                  <span className="font-medium">45</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Active</span>
                  <span className="font-medium">2 hours ago</span>
                </div>
              </div>
            </div>

            {/* Privacy Status Card */}
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy Status
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Mood Sharing</span>
                  <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                    Enabled
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Conversation Sharing</span>
                  <span className="text-sm bg-red-100 text-red-800 px-2 py-1 rounded">
                    Disabled
                  </span>
                </div>
                <button 
                  onClick={() => setActiveTab('privacy')}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Manage Privacy Settings
                </button>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Mood History Tab */}
        <TabsContent value="moods" className="mt-6">
          <MoodHistory studentId={studentId} />
        </TabsContent>

        {/* Privacy Tab - Feature 5 Integration */}
        <TabsContent value="privacy" className="mt-6">
          <PrivacyTab 
            studentId={studentId}
            currentUserId={currentUser.id}
            currentUserRole={currentUser.role}
          />
        </TabsContent>

        {/* Access Logs Tab - Feature 5 Integration */}
        <TabsContent value="logs" className="mt-6">
          <div className="bg-white rounded-lg border shadow-sm">
            {isInstitutionAdmin ? (
              <PrivacyTab 
                studentId={studentId}
                currentUserId={currentUser.id}
                currentUserRole={currentUser.role}
              />
            ) : (
              <div className="p-8 text-center">
                <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  Access logs are only available to institution administrators
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Example usage in a parent component or route
export const StudentDashboardPage: React.FC = () => {
  // This would typically come from routing and authentication context
  const studentId = "student123";
  const currentUser = {
    id: "user456",
    role: "institution",
    name: "Admin User"
  };
  const studentInfo = {
    name: "Priya Sharma",
    email: "priya.sharma@example.com",
    institution: "Delhi University"
  };

  return (
    <StudentDashboard 
      studentId={studentId}
      currentUser={currentUser}
      studentInfo={studentInfo}
    />
  );
};
