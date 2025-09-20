/**
 * Access Logs Component for Feature 5
 * Displays access history for a student's data
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { History, Shield, User, Clock, Activity } from 'lucide-react';
import { format } from 'date-fns';

interface AccessLogEntry {
  log_id: string;
  resource: string;
  action: string;
  performed_by: string;
  performed_by_role: string;
  timestamp: string;
  metadata: Record<string, string>;
}

interface AccessLogsProps {
  studentId: string;
}

export const AccessLogs: React.FC<AccessLogsProps> = ({ studentId }) => {
  const [logs, setLogs] = useState<AccessLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadAccessLogs();
  }, [studentId]);

  const loadAccessLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/students/${studentId}/access-logs?limit=50`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
      } else if (response.status === 403) {
        toast({
          title: "Access Denied",
          description: "You don't have permission to view access logs.",
          variant: "destructive"
        });
      } else {
        throw new Error('Failed to load access logs');
      }
    } catch (error) {
      console.error('Error loading access logs:', error);
      toast({
        title: "Error",
        description: "Failed to load access logs.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getResourceIcon = (resource: string) => {
    switch (resource) {
      case 'moods':
        return <Activity className="h-4 w-4" />;
      case 'conversations':
        return <History className="h-4 w-4" />;
      case 'privacy_settings':
        return <Shield className="h-4 w-4" />;
      case 'access_logs':
        return <User className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getActionColor = (action: string) => {
    if (action.includes('denied')) return 'destructive';
    if (action.includes('error')) return 'destructive';
    if (action.includes('update')) return 'default';
    if (action.includes('view')) return 'secondary';
    return 'outline';
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'institution':
        return 'bg-blue-100 text-blue-800';
      case 'student':
        return 'bg-green-100 text-green-800';
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return timestamp;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Access History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          Access History
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Log of who accessed this student's data and when
        </p>
      </CardHeader>
      <CardContent>
        {logs.length === 0 ? (
          <div className="text-center py-8">
            <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-muted-foreground">No access logs found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.log_id}
                className="flex items-start gap-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="p-2 bg-gray-100 rounded-lg">
                  {getResourceIcon(log.resource)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium capitalize">
                      {log.resource.replace('_', ' ')}
                    </span>
                    <Badge variant={getActionColor(log.action)}>
                      {log.action}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                    <User className="h-3 w-3" />
                    <span>User ID: {log.performed_by}</span>
                    <span className={`px-2 py-1 rounded text-xs ${getRoleColor(log.performed_by_role)}`}>
                      {log.performed_by_role}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>{formatTimestamp(log.timestamp)}</span>
                  </div>
                  
                  {/* Show metadata if available */}
                  {Object.keys(log.metadata).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      <details className="cursor-pointer">
                        <summary className="hover:text-gray-800">
                          View details
                        </summary>
                        <div className="mt-1 pl-4 border-l-2 border-gray-200">
                          {Object.entries(log.metadata).map(([key, value]) => (
                            <div key={key} className="flex gap-2">
                              <span className="font-medium">{key}:</span>
                              <span>{value}</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Privacy Notice */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <Shield className="h-4 w-4 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-blue-800">Access Transparency</p>
              <p className="text-blue-700 mt-1">
                All access to student data is automatically logged for accountability 
                and privacy protection. Students can request explanations for any 
                access to their information.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
