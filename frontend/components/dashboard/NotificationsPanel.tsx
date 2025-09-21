"use client";

import { useEffect, useState } from 'react';
import { NotificationItem, NotificationsListResponse } from '@/types/notifications';
import { AlertTriangle, CheckCircle, Bell } from 'lucide-react';

export default function NotificationsPanel() {
    const [items, setItems] = useState<NotificationItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchNotifications = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/v1/notifications/institution', { credentials: 'include' });
            if (!res.ok) {
                throw new Error(`Failed to load notifications (${res.status})`);
            }
            const data: NotificationsListResponse = await res.json();
            setItems(data.notifications || []);
        } catch (e: any) {
            setError(e.message || 'Failed to load notifications');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotifications();
        const id = setInterval(fetchNotifications, 15000);
        return () => clearInterval(id);
    }, []);

    const markRead = async (id: string) => {
        try {
            const res = await fetch(`/api/v1/notifications/${id}/read`, { method: 'POST', credentials: 'include' });
            if (res.ok) {
                setItems(prev => prev.map(it => it.notification_id === id ? { ...it, status: 'read' } : it));
            }
        } catch { }
    };

    return (
        <div className="bg-white rounded-lg shadow p-4 border">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <Bell className="h-5 w-5 text-indigo-600" />
                    <h3 className="font-semibold text-gray-900">Notifications</h3>
                </div>
                <button onClick={fetchNotifications} className="text-sm text-indigo-600 hover:underline">Refresh</button>
            </div>

            {loading && <div className="text-sm text-gray-500">Loading…</div>}
            {error && <div className="text-sm text-red-600">{error}</div>}

            {!loading && !error && items.length === 0 && (
                <div className="text-sm text-gray-500">No notifications</div>
            )}

            <ul className="space-y-3 max-h-80 overflow-y-auto">
                {items.map(n => (
                    <li key={n.notification_id} className="border rounded p-3 flex items-start justify-between">
                        <div className="flex items-start gap-3">
                            <AlertTriangle className={`h-5 w-5 ${n.severity === 'high' ? 'text-red-600' : n.severity === 'medium' ? 'text-amber-600' : 'text-gray-400'}`} />
                            <div>
                                <div className="text-sm font-medium text-gray-900">
                                    {n.type === 'crisis' ? 'Crisis Alert' : 'Notification'} · {n.risk_level.toUpperCase()}
                                </div>
                                <div className="text-xs text-gray-600">Student ID: {n.user_id} · Score: {n.risk_score}</div>
                                {n.reason && <div className="text-xs text-gray-500 mt-1">{n.reason}</div>}
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {n.status === 'unread' ? (
                                <button onClick={() => markRead(n.notification_id)} className="text-xs text-indigo-600 hover:underline">Mark read</button>
                            ) : (
                                <span className="text-xs text-gray-500 flex items-center gap-1"><CheckCircle className="h-3 w-3" /> Read</span>
                            )}
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}
