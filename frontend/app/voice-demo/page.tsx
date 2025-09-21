/**
 * Voice Demo Page - Redirect to Voice Messaging
 * 
 * This page redirects users to the new voice messaging interface
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Voice Demo Page - Redirect to Voice Messaging
 */
export default function VoiceDemo() {
    const router = useRouter();

    useEffect(() => {
        // Redirect to the new voice messaging page
        router.replace('/voice-messaging');
    }, [router]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Redirecting to Voice Messaging...</p>
            </div>
        </div>
    );
}
