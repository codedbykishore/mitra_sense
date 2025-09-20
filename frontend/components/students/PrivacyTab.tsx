/**
 * Privacy Tab Component for Feature 5
 * Combines Privacy Settings and Access Logs into a unified tab view
 */

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { PrivacySettings } from './PrivacySettings';
import { AccessLogs } from './AccessLogs';
import { Shield, History } from 'lucide-react';

interface PrivacyTabProps {
  studentId: string;
  currentUserId?: string;
  currentUserRole?: string;
}

export const PrivacyTab: React.FC<PrivacyTabProps> = ({ 
  studentId, 
  currentUserId,
  currentUserRole 
}) => {
  const [activeTab, setActiveTab] = useState('settings');
  
  // Determine if this is the user's own profile
  const isOwnProfile = currentUserId === studentId;
  
  // Only institution role can view access logs
  const canViewAccessLogs = currentUserRole === 'institution';

  return (
    <div className="w-full">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Privacy Settings
          </TabsTrigger>
          <TabsTrigger 
            value="logs" 
            className="flex items-center gap-2"
            disabled={!canViewAccessLogs}
          >
            <History className="h-4 w-4" />
            Access Logs
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="settings" className="mt-6">
          <PrivacySettings 
            studentId={studentId}
            isOwnProfile={isOwnProfile}
          />
        </TabsContent>
        
        <TabsContent value="logs" className="mt-6">
          {canViewAccessLogs ? (
            <AccessLogs studentId={studentId} />
          ) : (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-muted-foreground">
                Access logs are only available to institution administrators
              </p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};
