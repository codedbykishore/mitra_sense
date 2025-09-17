/**
 * VoiceChatDemo - Complete Voice Integration Demo
 * 
 * This page demonstrates the full ChatPane + VoiceCompanion integration
 * showcasing file-based voice interaction within the MITRA Sense chat UI.
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import ChatPane from '../../components/ChatPane';
import { useUser } from '../../hooks/useUser';
import { Settings, Info, Mic, MessageCircle } from 'lucide-react';

/**
 * Demo conversation for testing voice integration
 */
const createDemoConversation = () => ({
    id: 'voice-demo-conversation',
    title: 'Voice Chat Demo',
    messages: [
        {
            id: 'demo-1',
            role: 'assistant',
            content: 'Hello! I\'m MITRA, your mental health companion. You can chat with me using text or voice. Click the microphone button to try voice interaction.',
            timestamp: new Date(Date.now() - 60000),
        },
        {
            id: 'demo-2',
            role: 'user',
            content: 'Hi MITRA, I\'d like to try the voice feature.',
            timestamp: new Date(Date.now() - 30000),
        },
        {
            id: 'demo-3',
            role: 'assistant',
            content: 'Great! Voice interaction allows for more natural conversation and includes emotion analysis. I can detect stress levels and provide culturally appropriate support in Hindi or English.',
            timestamp: new Date(Date.now() - 15000),
        }
    ],
    messageCount: 3,
});

/**
 * Voice Chat Demo Page Component
 */
export default function VoiceChatDemo() {
    const { user, loading } = useUser();
    const [conversation, setConversation] = useState(createDemoConversation());
    const [isThinking, setIsThinking] = useState(false);
    const [isClient, setIsClient] = useState(false);

    // Ensure hydration compatibility
    useEffect(() => {
        setIsClient(true);
    }, []);
    const [demoSettings, setDemoSettings] = useState({
        culturalContext: {
            language: 'en-US',
            familyContext: 'individual',
            greetingStyle: 'informal',
        },
        crisisThreshold: 0.7,
        showTechnicalInfo: false,
    });

    /**
     * Handle new text messages
     */
    const handleSend = useCallback(async (text: string) => {
        console.log('Sending message:', text);

        // Add user message
        const userMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: text,
            timestamp: new Date(),
        };

        setConversation(prev => ({
            ...prev,
            messages: [...prev.messages, userMessage],
            messageCount: prev.messageCount + 1,
        }));

        // Simulate AI thinking
        setIsThinking(true);

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Add AI response
        const aiMessage = {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: `I understand you said: "${text}". This is a demo response. In the real MITRA system, this would be processed through our culturally-aware AI with RAG capabilities and crisis detection.`,
            timestamp: new Date(),
        };

        setConversation(prev => ({
            ...prev,
            messages: [...prev.messages, aiMessage],
            messageCount: prev.messageCount + 1,
        }));

        setIsThinking(false);
    }, []);

    /**
     * Handle message editing
     */
    const handleEditMessage = useCallback((messageId: string, newContent: string) => {
        console.log('Editing message:', messageId, newContent);

        setConversation(prev => ({
            ...prev,
            messages: prev.messages.map(msg =>
                msg.id === messageId ? { ...msg, content: newContent } : msg
            ),
        }));
    }, []);

    /**
     * Handle message resending
     */
    const handleResendMessage = useCallback((messageId: string) => {
        console.log('Resending message:', messageId);

        const message = conversation.messages.find(msg => msg.id === messageId);
        if (message && message.content) {
            handleSend(message.content);
        }
    }, [conversation.messages, handleSend]);

    /**
     * Handle thinking pause
     */
    const handlePauseThinking = useCallback(() => {
        console.log('Pausing AI thinking');
        setIsThinking(false);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading MITRA Voice Chat Demo...</p>
                </div>
            </div>
        );
    }

    if (!isClient) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
                <div className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex items-center justify-between h-16">
                            <div className="flex items-center">
                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm font-bold mr-3">
                                    M
                                </div>
                                <div>
                                    <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                        MITRA Voice Chat Demo
                                    </h1>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        Loading...
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* Header */}
            <div className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm font-bold mr-3">
                                M
                            </div>
                            <div>
                                <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                    MITRA Voice Chat Demo
                                </h1>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Complete voice integration with ChatPane
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                                {user ? `Welcome, ${(user as any).name || 'User'}` : 'Demo Mode'}
                            </div>
                            <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                                <Settings className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto h-[calc(100vh-4rem)] flex">
                {/* Settings Sidebar */}
                {demoSettings.showTechnicalInfo && (
                    <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 overflow-y-auto">
                        <div className="flex items-center mb-4">
                            <Info className="h-4 w-4 text-blue-600 mr-2" />
                            <h3 className="font-medium text-gray-900 dark:text-gray-100">Demo Settings</h3>
                        </div>

                        <div className="space-y-4 text-sm">
                            <div>
                                <label className="block text-gray-700 dark:text-gray-300 mb-1">Language</label>
                                <select
                                    value={demoSettings.culturalContext.language}
                                    onChange={(e) => setDemoSettings(prev => ({
                                        ...prev,
                                        culturalContext: {
                                            ...prev.culturalContext,
                                            language: e.target.value
                                        }
                                    }))}
                                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                                >
                                    <option value="en-US">English (US)</option>
                                    <option value="hi-IN">Hindi (India)</option>
                                    <option value="ta-IN">Tamil (India)</option>
                                    <option value="te-IN">Telugu (India)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-gray-700 dark:text-gray-300 mb-1">Family Context</label>
                                <select
                                    value={demoSettings.culturalContext.familyContext}
                                    onChange={(e) => setDemoSettings(prev => ({
                                        ...prev,
                                        culturalContext: {
                                            ...prev.culturalContext,
                                            familyContext: e.target.value
                                        }
                                    }))}
                                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                                >
                                    <option value="individual">Individual</option>
                                    <option value="family-aware">Family Aware</option>
                                    <option value="elder-present">Elder Present</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-gray-700 dark:text-gray-300 mb-1">
                                    Crisis Threshold ({Math.round(demoSettings.crisisThreshold * 100)}%)
                                </label>
                                <input
                                    type="range"
                                    min="0.3"
                                    max="0.9"
                                    step="0.1"
                                    value={demoSettings.crisisThreshold}
                                    onChange={(e) => setDemoSettings(prev => ({
                                        ...prev,
                                        crisisThreshold: parseFloat(e.target.value)
                                    }))}
                                    className="w-full"
                                />
                            </div>
                        </div>

                        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">How to Test Voice</h4>
                            <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                                <li>• Click the microphone button in the composer</li>
                                <li>• Record a voice message (push-to-talk)</li>
                                <li>• Audio uploads to /api/v1/voice/pipeline/audio</li>
                                <li>• Receive transcription + AI response + TTS audio</li>
                                <li>• Emotion analysis and crisis detection active</li>
                            </ul>
                        </div>
                    </div>
                )}

                {/* Main Chat Interface */}
                <div className="flex-1 bg-white dark:bg-gray-900">
                    {(ChatPane as any)({
                        conversation,
                        onSend: handleSend,
                        onEditMessage: handleEditMessage,
                        onResendMessage: handleResendMessage,
                        isThinking,
                        onPauseThinking: handlePauseThinking,
                    })}
                </div>

                {/* Feature Status Panel */}
                <div className="w-80 bg-gray-50 dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto">
                    <div className="flex items-center mb-4">
                        <Mic className="h-4 w-4 text-green-600 mr-2" />
                        <h3 className="font-medium text-gray-900 dark:text-gray-100">Voice Integration Status</h3>
                    </div>

                    <div className="space-y-3 text-sm">
                        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/20 rounded">
                            <span className="text-green-800 dark:text-green-200">VoiceCompanion</span>
                            <span className="text-green-600 text-xs">✓ Integrated</span>
                        </div>

                        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/20 rounded">
                            <span className="text-green-800 dark:text-green-200">Push-to-Talk</span>
                            <span className="text-green-600 text-xs">✓ Active</span>
                        </div>

                        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/20 rounded">
                            <span className="text-green-800 dark:text-green-200">File Upload</span>
                            <span className="text-green-600 text-xs">✓ Ready</span>
                        </div>

                        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/20 rounded">
                            <span className="text-green-800 dark:text-green-200">Crisis Detection</span>
                            <span className="text-green-600 text-xs">✓ Monitoring</span>
                        </div>

                        <div className="flex items-center justify-between p-2 bg-green-100 dark:bg-green-900/20 rounded">
                            <span className="text-green-800 dark:text-green-200">Accessibility</span>
                            <span className="text-green-600 text-xs">✓ ARIA Labels</span>
                        </div>

                        <div className="flex items-center justify-between p-2 bg-blue-100 dark:bg-blue-900/20 rounded">
                            <span className="text-blue-800 dark:text-blue-200">Backend API</span>
                            <span className="text-blue-600 text-xs">⚠ Demo Mode</span>
                        </div>
                    </div>

                    <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                        <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Integration Complete!</h4>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                            VoiceCompanion is fully integrated into ChatPane with:
                        </p>
                        <ul className="text-xs text-gray-600 dark:text-gray-400 mt-2 space-y-1">
                            <li>✓ File-based recording</li>
                            <li>✓ Backend integration</li>
                            <li>✓ TTS playback</li>
                            <li>✓ Crisis detection</li>
                            <li>✓ Cultural context</li>
                            <li>✓ Error handling</li>
                            <li>✓ Accessibility</li>
                        </ul>
                    </div>

                    <button
                        onClick={() => setDemoSettings(prev => ({
                            ...prev,
                            showTechnicalInfo: !prev.showTechnicalInfo
                        }))}
                        className="mt-4 w-full p-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        {demoSettings.showTechnicalInfo ? 'Hide' : 'Show'} Technical Info
                    </button>
                </div>
            </div>
        </div>
    );
}