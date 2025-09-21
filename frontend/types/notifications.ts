export type NotificationStatus = 'unread' | 'read' | 'acknowledged';

export interface NotificationItem {
    notification_id: string;
    institution_id: string;
    user_id: string;
    type: 'crisis' | 'info' | 'system';
    severity: 'low' | 'medium' | 'high';
    risk_score: number;
    risk_level: 'low' | 'medium' | 'high';
    reason?: string | null;
    status: NotificationStatus;
    created_at?: string | null;
    metadata?: Record<string, string>;
}

export interface NotificationsListResponse {
    notifications: NotificationItem[];
}
