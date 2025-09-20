/**
 * Privacy Settings Component for Feature 5
 * Allows students to control sharing of their moods and conversations
 */

import React, { useState, useEffect } from 'react';
import { Switch } from '../ui/switch';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { useToast } from '../../hooks/use-toast';
import { Shield, Lock, Eye, EyeOff } from 'lucide-react';

interface PrivacyFlags {
  share_moods: boolean;
  share_conversations: boolean;
}

interface PrivacySettingsProps {
  studentId: string;
  isOwnProfile?: boolean;
}

export const PrivacySettings: React.FC<PrivacySettingsProps> = ({ 
  studentId, 
  isOwnProfile = false 
}) => {
  const [privacyFlags, setPrivacyFlags] = useState<PrivacyFlags>({
    share_moods: true,
    share_conversations: true
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadPrivacyFlags();
  }, [studentId]);

  const loadPrivacyFlags = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/students/${studentId}/privacy`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setPrivacyFlags(data.privacy_flags);
      } else if (response.status === 403) {
        toast({
          title: "Access Denied",
          description: "You don't have permission to view privacy settings.",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Error loading privacy flags:', error);
      toast({
        title: "Error",
        description: "Failed to load privacy settings.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrivacyChange = (key: keyof PrivacyFlags, value: boolean) => {
    setPrivacyFlags(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const savePrivacySettings = async () => {
    setSaving(true);
    try {
      const response = await fetch(`/api/v1/students/${studentId}/privacy`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          privacy_flags: privacyFlags
        })
      });

      if (response.ok) {
        toast({
          title: "Privacy Settings Updated",
          description: "Your privacy preferences have been saved.",
          variant: "default"
        });
      } else if (response.status === 403) {
        toast({
          title: "Access Denied",
          description: "You don't have permission to update privacy settings.",
          variant: "destructive"
        });
      } else {
        throw new Error('Failed to update privacy settings');
      }
    } catch (error) {
      console.error('Error saving privacy settings:', error);
      toast({
        title: "Error",
        description: "Failed to save privacy settings.",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Privacy Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Privacy Settings
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Control who can access your information
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Mood Sharing Setting */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              {privacyFlags.share_moods ? (
                <Eye className="h-4 w-4 text-blue-600" />
              ) : (
                <EyeOff className="h-4 w-4 text-gray-600" />
              )}
            </div>
            <div>
              <h3 className="font-medium">Share Mood Data</h3>
              <p className="text-sm text-muted-foreground">
                Allow facilitators and administrators to view your mood entries
              </p>
            </div>
          </div>
          <Switch
            checked={privacyFlags.share_moods}
            onCheckedChange={(checked) => handlePrivacyChange('share_moods', checked)}
            disabled={!isOwnProfile}
          />
        </div>

        {/* Conversation Sharing Setting */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              {privacyFlags.share_conversations ? (
                <Eye className="h-4 w-4 text-green-600" />
              ) : (
                <EyeOff className="h-4 w-4 text-gray-600" />
              )}
            </div>
            <div>
              <h3 className="font-medium">Share Conversations</h3>
              <p className="text-sm text-muted-foreground">
                Allow facilitators and administrators to view your chat history
              </p>
            </div>
          </div>
          <Switch
            checked={privacyFlags.share_conversations}
            onCheckedChange={(checked) => handlePrivacyChange('share_conversations', checked)}
            disabled={!isOwnProfile}
          />
        </div>

        {/* Privacy Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <Lock className="h-4 w-4 text-yellow-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-yellow-800">Privacy Notice</p>
              <p className="text-yellow-700 mt-1">
                Even when sharing is disabled, emergency situations may require access 
                to your data for safety purposes. All access is logged and monitored.
              </p>
            </div>
          </div>
        </div>

        {/* Save Button - Only show for own profile */}
        {isOwnProfile && (
          <div className="flex justify-end pt-4 border-t">
            <Button 
              onClick={savePrivacySettings}
              disabled={saving}
              className="min-w-24"
            >
              {saving ? "Saving..." : "Save Settings"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
