/**
 * VoiceMessaging - Pure Voice Communication Interface
 * 
 * WhatsApp-like voice messaging interface for MITRA Sense mental health platform.
 * Features file-based audio messages, playback controls, and emotion analysis.
 */

'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useUser } from '../../hooks/useUser';
import { Play, Pause, Phone, AlertTriangle } from 'lucide-react';
import { VoiceRecorder } from '../../components/voice/VoiceRecorder';
import { useSpeechLoop } from '../../hooks/useSpeechLoop';
import type { VoiceEmotionAnalysis } from '../../components/voice/types';

/**
 * Voice message structure for the messaging interface
 */
interface VoiceMessage {
    id: string;
    role: 'user' | 'assistant';
    audioUrl: string;
    audioBlob?: Blob;
    duration: number;
    transcription?: string;
    emotion?: VoiceEmotionAnalysis;
    timestamp: Date;
    isPlaying?: boolean;
    crisisScore?: number;
}

/**
 * Minimal Voice Message Bubble Component - Just Play Button and Duration
 */
const VoiceMessageBubble: React.FC<{
    message: VoiceMessage;
    onPlay: (id: string) => void;
    onPause: (id: string) => void;
}> = ({ message, onPlay, onPause }) => {
    const audioRef = useRef<HTMLAudioElement>(null);

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handlePlayPause = () => {
        if (message.isPlaying) {
            onPause(message.id);
        } else {
            onPlay(message.id);
        }
    };

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const handleEnded = () => onPause(message.id);
        audio.addEventListener('ended', handleEnded);

        return () => {
            audio.removeEventListener('ended', handleEnded);
        };
    }, [message.id, onPause]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        if (message.isPlaying) {
            audio.play().catch((error) => {
                console.error('Audio playback failed:', error);
                onPause(message.id);
            });
        } else {
            audio.pause();
        }
    }, [message.isPlaying, message.id, onPause]);

    const isUser = message.role === 'user';
    const bubbleClass = isUser 
        ? 'bg-blue-500 text-white ml-auto' 
        : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white mr-auto';

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`px-3 py-2 rounded-xl ${bubbleClass}`}>
                {/* Simple Audio Player - Just Play Button and Duration */}
                <div className="flex items-center gap-3">
                    <button
                        onClick={handlePlayPause}
                        className={`p-2 rounded-full transition-colors ${
                            isUser 
                                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                                : 'bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200'
                        }`}
                        aria-label={message.isPlaying ? 'Pause voice message' : 'Play voice message'}
                    >
                        {message.isPlaying ? (
                            <Pause className="h-4 w-4" />
                        ) : (
                            <Play className="h-4 w-4 ml-0.5" />
                        )}
                    </button>

                    {/* Duration Display */}
                    <span className="text-sm font-medium">
                        {formatDuration(message.duration)}
                    </span>
                </div>

                {/* Hidden audio element */}
                <audio
                    ref={audioRef}
                    src={message.audioUrl}
                    preload="metadata"
                    className="hidden"
                />
            </div>
        </div>
    );
};

/**
 * Main Voice Messaging Interface
 */
export default function VoiceMessaging() {
    const { user, loading } = useUser();
    const [messages, setMessages] = useState<VoiceMessage[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);
    const [crisisAlert, setCrisisAlert] = useState<{
        score: number;
        actions: string[];
        timestamp: Date;
    } | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const screenReaderRef = useRef<HTMLDivElement>(null);

    // Initialize speech loop for backend communication
    const {
        state,
        error,
        currentTranscription,
        currentResponse,
        currentEmotion,
        processAudioBlob,
        resetSession,
        getConversationHistory
    } = useSpeechLoop({
        culturalContext: {
            language: (user as any)?.preferredLanguage || 'en-US',
            familyContext: 'individual',
            greetingStyle: 'informal'
        },
        onInteractionComplete: (response) => {
            // Handle completed interaction
            const userMessage: VoiceMessage = {
                id: `user-${Date.now()}`,
                role: 'user',
                audioUrl: '', // User's original audio would be stored here
                duration: 0, // Would come from recording
                transcription: response.transcription?.text,
                emotion: response.emotion,
                timestamp: new Date()
            };

            const assistantMessage: VoiceMessage = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                audioUrl: response.ttsAudio?.url || '',
                duration: response.ttsAudio?.duration || 0,
                transcription: response.aiResponse?.text,
                emotion: response.emotion,
                crisisScore: response.aiResponse?.crisisScore,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, userMessage, assistantMessage]);

            // Handle crisis detection
            if (response.aiResponse?.crisisScore && response.aiResponse.crisisScore > 0.7) {
                setCrisisAlert({
                    score: response.aiResponse.crisisScore,
                    actions: response.aiResponse.suggestedActions || ['Contact Tele MANAS (14416)'],
                    timestamp: new Date()
                });
                
                // Announce crisis to screen readers
                announceToScreenReader(`Crisis level detected. Crisis score: ${Math.round(response.aiResponse.crisisScore * 100)}%. Immediate support is available.`);
            }

            // Announce new message for accessibility
            announceToScreenReader(`New voice message from MITRA received. Duration: ${Math.round(assistantMessage.duration)} seconds.`);
        }
    });

    // Auto scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // The onInteractionComplete callback in useSpeechLoop config handles successful voice processing

    // Screen reader announcements
    const announceToScreenReader = useCallback((message: string) => {
        if (screenReaderRef.current) {
            screenReaderRef.current.textContent = message;
            setTimeout(() => {
                if (screenReaderRef.current) {
                    screenReaderRef.current.textContent = '';
                }
            }, 1000);
        }
    }, []);

    // Handle voice recording completion
    const handleRecordingComplete = useCallback(async (audioBlob: Blob, duration: number) => {
        setIsRecording(false);
        
        try {
            announceToScreenReader(`Voice recording completed. Duration: ${Math.round(duration)} seconds. Processing...`);
            await processAudioBlob(audioBlob, duration);
        } catch (error) {
            console.error('Voice processing failed:', error);
            announceToScreenReader('Voice processing failed. Please try again.');
        }
    }, [processAudioBlob, announceToScreenReader]);

    // Handle recording errors
    const handleRecordingError = useCallback((errorType: string, message: string) => {
        console.error('Recording error:', { errorType, message });
        setIsRecording(false);
        announceToScreenReader(`Recording error: ${message}`);
    }, [announceToScreenReader]);

    // Audio playback controls
    const handlePlay = useCallback((messageId: string) => {
        setCurrentPlayingId(messageId);
        setMessages(prev => prev.map(msg => ({
            ...msg,
            isPlaying: msg.id === messageId
        })));
    }, []);

    const handlePause = useCallback((messageId: string) => {
        setCurrentPlayingId(null);
        setMessages(prev => prev.map(msg => ({
            ...msg,
            isPlaying: false
        })));
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading MITRA Voice Messaging...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* Screen reader announcements */}
            <div
                ref={screenReaderRef}
                aria-live="polite"
                aria-atomic="true"
                className="sr-only"
            />

            {/* Header */}
            <div className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-lg font-bold mr-3">
                                M
                            </div>
                            <div>
                                <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                                    Voice Messaging with MITRA
                                </h1>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Speak naturally, I'm here to listen
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                                {user ? `${(user as any).name || 'User'}` : 'Voice Mode'}
                            </div>
                            {state !== 'idle' && (
                                <div className="flex items-center gap-2 text-sm text-blue-600">
                                    <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse"></div>
                                    <span className="capitalize">{state}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Crisis Alert Banner */}
            {crisisAlert && (
                <div
                    className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-4"
                    role="alert"
                    aria-live="assertive"
                >
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20">
                        <div className="flex items-start">
                            <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                            <div className="flex-1">
                                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                                    Crisis Level Detected ({Math.round(crisisAlert.score * 100)}%)
                                </h3>
                                <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                                    Immediate support is available. You are not alone.
                                </p>
                                <div className="mt-3 flex items-center gap-3">
                                    <button
                                        onClick={() => window.open('tel:14416')}
                                        className="inline-flex items-center gap-1 rounded bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
                                    >
                                        <Phone className="h-3 w-3" />
                                        Call Tele MANAS (14416)
                                    </button>
                                    <button
                                        onClick={() => setCrisisAlert(null)}
                                        className="text-xs text-red-600 hover:text-red-800 dark:text-red-400"
                                    >
                                        Acknowledge
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Messages Container */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg min-h-[600px] flex flex-col">
                    {/* Messages Area */}
                    <div className="flex-1 p-6 overflow-y-auto">
                        {messages.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                                <div className="flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-3xl font-bold">
                                    M
                                </div>
                                <div className="space-y-4">
                                    <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                                        Start a Voice Conversation
                                    </h2>
                                    <p className="text-lg text-gray-600 dark:text-gray-400">
                                        Press and hold the microphone to record your voice message
                                    </p>
                                    <div className="space-y-2 text-sm text-gray-500 dark:text-gray-400 max-w-md">
                                        <p className="italic">"I'm here to listen and understand"</p>
                                        <p className="italic">"Speak in Hindi or English, whatever feels natural"</p>
                                        <p className="italic">"Your mental health matters"</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            messages.map((message) => (
                                <VoiceMessageBubble
                                    key={message.id}
                                    message={message}
                                    onPlay={handlePlay}
                                    onPause={handlePause}
                                />
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Recording Interface */}
                    <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                        <div className="flex items-center justify-center">
                            <VoiceRecorder
                                onRecordingComplete={handleRecordingComplete}
                                onError={handleRecordingError}
                                maxDuration={180} // 3 minutes max
                                className="flex items-center justify-center"
                            />
                        </div>

                        {/* Processing Status */}
                        {state !== 'idle' && (
                            <div className="mt-4 text-center">
                                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                                    <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse"></div>
                                    <span className="text-sm capitalize">
                                        {state === 'processing' ? 'Processing your voice...' : 
                                         state === 'uploading' ? 'Uploading...' :
                                         state === 'playing' ? 'Playing response...' : state}
                                    </span>
                                </div>
                            </div>
                        )}

                        {/* Error Display */}
                        {error && (
                            <div className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="h-4 w-4 text-red-500" />
                                    <span className="text-sm text-red-700 dark:text-red-300">{error.message}</span>
                                    <button
                                        onClick={resetSession}
                                        className="ml-auto text-xs text-red-600 hover:text-red-800 dark:text-red-400"
                                    >
                                        Try Again
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
