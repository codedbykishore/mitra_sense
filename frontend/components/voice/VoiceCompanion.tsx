/**
 * VoiceCompanion - Complete Voice Interaction Component
 * 
 * This component integrates VoiceRecorder, useSpeechLoop, and VoicePlayer
 * to create a complete file-based push-to-talk voice interaction system
 * for MITRA Sense mental health platform.
 * 
 * Features:
 * - File-based recording with VoiceRecorder
 * - Backend integration via useSpeechLoop
 * - TTS playback with VoicePlayer
 * - Crisis detection and cultural context
 * - Accessibility and ChatPane integration
 */

'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { VoiceRecorder } from './VoiceRecorder';
import VoicePlayer, { VoicePlayerRef } from './VoicePlayer';
import { useSpeechLoop } from '../../hooks/useSpeechLoop';
import { VoiceRecordingError, VoiceLanguageCode, VoiceEmotionAnalysis } from './types';
import {
    Mic,
    MicOff,
    Volume2,
    VolumeX,
    AlertTriangle,
    Heart,
    Phone,
    RotateCcw,
    Clock,
    User,
    Bot,
    Activity,
    Globe,
    Shield,
    HelpCircle,
    Square
} from 'lucide-react';

/**
 * Props for VoiceCompanion component
 */
export interface VoiceCompanionProps {
    /** Authentication token for API calls */
    authToken?: string;

    /** Cultural context for voice interactions */
    culturalContext?: {
        language: VoiceLanguageCode;
        familyContext: 'individual' | 'family-aware' | 'elder-present';
        greetingStyle: 'formal' | 'informal' | 'traditional';
    };

    /** Crisis detection threshold (0-1, default 0.7) */
    crisisThreshold?: number;

    /** Callback when crisis is detected */
    onCrisisDetected?: (crisisScore: number, suggestedActions: string[]) => void;

    /** Callback when voice interaction completes */
    onInteractionComplete?: (transcription: string, response: string, emotion: VoiceEmotionAnalysis) => void;

    /** Enable integration with ChatPane styling */
    chatPaneMode?: boolean;

    /** Show detailed controls and info */
    showAdvancedControls?: boolean;

    /** Custom CSS classes */
    className?: string;

    /** Disabled state */
    disabled?: boolean;
}

/**
 * VoiceCompanion Component
 * 
 * Complete voice interaction interface that combines:
 * - VoiceRecorder for audio capture
 * - useSpeechLoop for backend processing
 * - VoicePlayer for TTS playback
 * - Crisis detection and safety features
 * - Cultural adaptation for Hindi/English
 * - ChatPane-compatible UI integration
 * - Full accessibility support
 */
export const VoiceCompanion: React.FC<VoiceCompanionProps> = ({
    authToken,
    culturalContext,
    crisisThreshold = 0.7,
    onCrisisDetected,
    onInteractionComplete,
    chatPaneMode = false,
    showAdvancedControls = true,
    className = '',
    disabled = false,
}) => {
    // Local state for UI management
    const [showTranscription, setShowTranscription] = useState(true);
    const [showEmotionDetails, setShowEmotionDetails] = useState(false);
    const [audioSource, setAudioSource] = useState<string | Blob | null>(null);
    const [lastCrisisAlert, setLastCrisisAlert] = useState<Date | null>(null);

    // Refs for component control
    const voicePlayerRef = useRef<VoicePlayerRef>(null);
    const announceRef = useRef<HTMLDivElement>(null);

    // Initialize speech loop hook
    const {
        state,
        isRecording,
        isProcessing,
        isPlaying,
        error,
        currentTranscription,
        currentResponse,
        currentEmotion,
        conversationId,
        sessionId,
        startRecording,
        stopRecording,
        cancelCurrent,
        clearError,
        resetSession,
        processAudioBlob,
        getConversationHistory,
    } = useSpeechLoop({
        authToken,
        culturalContext,
        autoPlayResponses: false, // We'll control playback manually
        enableContextPersistence: true,

        // Handle successful interactions
        onInteractionComplete: (response) => {
            console.log('Voice interaction completed:', response);

            // Set audio source for VoicePlayer
            if (response.ttsAudio.blob || response.ttsAudio.url) {
                const audioSrc = response.ttsAudio.blob || response.ttsAudio.url!;
                setAudioSource(audioSrc);
                
                // Auto-play the response
                setTimeout(() => {
                    voicePlayerRef.current?.play();
                }, 100);
            }

            // Check for crisis indicators
            if (response.aiResponse.crisisScore >= crisisThreshold) {
                handleCrisisDetection(response.aiResponse.crisisScore, response.aiResponse.suggestedActions);
            }

            // Announce completion for screen readers
            announceToScreenReader(`Response received. ${response.emotion.primaryEmotion} detected.`);

            // Call external callback
            onInteractionComplete?.(
                response.transcription.text,
                response.aiResponse.text,
                response.emotion
            );
        },

        // Handle errors
        onError: (errorType, message, details) => {
            console.error('Speech loop error:', { errorType, message, details });
            announceToScreenReader(`Error: ${message}`);
        },

        // Handle state changes
        onStateChange: (newState) => {
            console.log('Speech state changed:', newState);
            
            // Announce state changes for accessibility
            switch (newState) {
                case 'recording':
                    announceToScreenReader('Recording started');
                    break;
                case 'processing':
                    announceToScreenReader('Processing audio');
                    break;
                case 'playing':
                    announceToScreenReader('Playing response');
                    break;
                case 'idle':
                    announceToScreenReader('Ready for next interaction');
                    break;
            }
        },
    });

    /**
     * Handle crisis detection with proper alerting
     */
    const handleCrisisDetection = useCallback((crisisScore: number, suggestedActions: string[]) => {
        const now = new Date();
        
        // Prevent spam alerts (max one per 30 seconds)
        if (lastCrisisAlert && (now.getTime() - lastCrisisAlert.getTime()) < 30000) {
            return;
        }
        
        setLastCrisisAlert(now);
        announceToScreenReader(`Crisis level detected. Immediate support available.`);
        
        onCrisisDetected?.(crisisScore, suggestedActions);
    }, [lastCrisisAlert, onCrisisDetected]);

    /**
     * Announce messages to screen readers
     */
    const announceToScreenReader = useCallback((message: string) => {
        if (announceRef.current) {
            announceRef.current.textContent = message;
            // Clear after announcement
            setTimeout(() => {
                if (announceRef.current) announceRef.current.textContent = '';
            }, 1000);
        }
    }, []);

    /**
     * Handle recording completion from VoiceRecorder
     */
    const handleRecordingComplete = useCallback((audioBlob: Blob, duration: number) => {
        // Stop any current playback to prevent interference
        if (isPlaying) {
            voicePlayerRef.current?.stop();
        }
        
        processAudioBlob(audioBlob, duration);
        announceToScreenReader(`Recording completed. Processing ${duration.toFixed(1)} seconds of audio.`);
    }, [processAudioBlob, isPlaying]);

    /**
     * Handle recording errors from VoiceRecorder
     */
    const handleRecordingError = useCallback((errorType: VoiceRecordingError, message: string) => {
        console.error('Recording error:', errorType, message);
        announceToScreenReader(`Recording error: ${message}`);
    }, []);

    /**
     * Handle VoicePlayer events
     */
    const handlePlaybackStart = useCallback(() => {
        announceToScreenReader('Response playback started');
    }, []);

    const handlePlaybackEnd = useCallback(() => {
        announceToScreenReader('Response playback completed');
        setAudioSource(null); // Clear audio source
    }, []);

    const handlePlaybackError = useCallback((error: any, message: string) => {
        console.error('Playback error:', error, message);
        announceToScreenReader(`Playback error: ${message}`);
    }, []);

    /**
     * Handle manual stop/cancel
     */
    const handleCancelInteraction = useCallback(() => {
        cancelCurrent();
        voicePlayerRef.current?.stop();
        setAudioSource(null);
        announceToScreenReader('Interaction cancelled');
    }, [cancelCurrent]);

    /**
     * Reset entire session
     */
    const handleResetSession = useCallback(() => {
        resetSession();
        voicePlayerRef.current?.stop();
        setAudioSource(null);
        setLastCrisisAlert(null);
        announceToScreenReader('New conversation started');
    }, [resetSession]);

    /**
     * Format emotion display with cultural context
     */
    const formatEmotion = (emotion: VoiceEmotionAnalysis | null) => {
        if (!emotion) return null;

        const emotionEmojis: Record<string, string> = {
            happy: '😊', sad: '😢', angry: '😠', anxious: '😰',
            calm: '😌', stressed: '😟', excited: '🤗', neutral: '😐',
            hopeful: '🙂', frustrated: '😤', worried: '😟', content: '😊'
        };

        const emoji = emotionEmojis[emotion.primaryEmotion.toLowerCase()] || '🤔';
        const confidence = Math.round(emotion.confidence * 100);

        return {
            emoji,
            text: emotion.primaryEmotion,
            confidence,
            stressLevel: emotion.stressLevel
        };
    };

    /**
     * Get cultural greeting based on context
     */
    const getCulturalGreeting = () => {
        const lang = culturalContext?.language || 'en-US';
        const style = culturalContext?.greetingStyle || 'informal';

        if (lang.startsWith('hi')) {
            switch (style) {
                case 'formal': return 'नमस्कार, MITRA आपकी सेवा में है';
                case 'traditional': return 'आदाब, MITRA आपका साथी है';
                default: return 'हैलो, MITRA से बात करें';
            }
        }

        switch (style) {
            case 'formal': return 'Welcome to MITRA Voice Companion';
            case 'traditional': return 'Greetings, MITRA is here to help';
            default: return 'Hi! Talk to MITRA';
        }
    };

    /**
     * Get crisis level styling
     */
    const getCrisisLevelStyling = (score: number) => {
        if (score >= crisisThreshold) return 'bg-red-100 border-red-300 text-red-800';
        if (score >= 0.4) return 'bg-yellow-100 border-yellow-300 text-yellow-800';
        return 'bg-green-100 border-green-300 text-green-800';
    };

    /**
     * Get current state information for UI
     */
    const getStateInfo = () => {
        const lang = culturalContext?.language?.startsWith('hi') ? 'hi' : 'en';
        
        const stateMessages = {
            hi: {
                idle: 'बात करने के लिए तैयार',
                recording: 'रिकॉर्ड हो रहा है...',
                uploading: 'भेज रहे हैं...',
                processing: 'समझ रहे हैं...',
                playing: 'जवाब दे रहे हैं...',
                error: 'समस्या है...'
            },
            en: {
                idle: 'Ready to listen',
                recording: 'Recording...',
                uploading: 'Uploading...',
                processing: 'Processing...',
                playing: 'Responding...',
                error: 'Error occurred...'
            }
        };

        const messages = stateMessages[lang];
        const message = messages[state] || messages.idle;
        
        return {
            message,
            color: state === 'error' ? 'text-red-600' : 
                   state === 'recording' ? 'text-red-500' :
                   state === 'processing' ? 'text-blue-500' :
                   state === 'playing' ? 'text-green-500' : 'text-gray-600',
            bgColor: state === 'error' ? 'bg-red-50' :
                     state === 'recording' ? 'bg-red-50' :
                     state === 'processing' ? 'bg-blue-50' :
                     state === 'playing' ? 'bg-green-50' : 'bg-gray-50'
        };
    };

    const stateInfo = getStateInfo();
    const emotionInfo = formatEmotion(currentEmotion);

    return (
        <div 
            className={`voice-companion ${chatPaneMode ? 'chat-pane-mode' : 'standalone-mode'} ${className}`}
            role="region"
            aria-label="Voice companion interface"
        >
            {/* Screen reader announcements */}
            <div 
                ref={announceRef}
                aria-live="polite"
                aria-atomic="true"
                className="sr-only"
            />

            {/* Header */}
            <div className={`${chatPaneMode ? 'p-3 border-b border-gray-200' : 'p-4 border-b border-gray-200 bg-gray-50'}`}>
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                            MITRA Voice
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            {getCulturalGreeting()}
                        </p>
                    </div>
                    
                    {/* Status Indicator */}
                    <div className={`flex items-center px-3 py-1 rounded-full text-sm ${stateInfo.bgColor} ${stateInfo.color}`}>
                        <Activity className="w-4 h-4 mr-1" />
                        {stateInfo.message}
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 border-l-4 border-red-400">
                    <div className="flex items-center">
                        <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                        <div>
                            <p className="text-red-800 font-medium">Error: {error.type}</p>
                            <p className="text-red-600 text-sm">{error.message}</p>
                        </div>
                        <button
                            onClick={clearError}
                            className="ml-auto text-red-500 hover:text-red-700"
                            aria-label="Clear error"
                        >
                            <Square className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Main Voice Interface */}
            <div className="p-4 space-y-4">
                
                {/* Voice Recorder */}
                <div className="flex justify-center">
                    <VoiceRecorder
                        onRecordingComplete={handleRecordingComplete}
                        onError={handleRecordingError}
                        disabled={disabled || isProcessing || isPlaying}
                        maxDuration={180}
                        className="voice-recorder-container"
                    />
                </div>

                {/* Control Buttons */}
                <div className="flex justify-center space-x-3">
                    {(isProcessing || isRecording || isPlaying) && (
                        <button
                            onClick={handleCancelInteraction}
                            className="flex items-center px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                            aria-label="Cancel current operation"
                        >
                            <Square className="w-4 h-4 mr-2" />
                            Cancel
                        </button>
                    )}
                    
                    <button
                        onClick={handleResetSession}
                        className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                        aria-label="Start new conversation"
                    >
                        <RotateCcw className="w-4 h-4 mr-2" />
                        New Chat
                    </button>
                </div>

                {/* Current Interaction Display */}
                {(currentTranscription || currentResponse) && (
                    <div className="space-y-4">
                        
                        {/* User's Transcription */}
                        {currentTranscription && showTranscription && (
                            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200">
                                <div className="flex items-center mb-2">
                                    <User className="w-4 h-4 text-blue-600 mr-2" />
                                    <h4 className="font-medium text-blue-800 dark:text-blue-200">
                                        {culturalContext?.language?.startsWith('hi') ? 'आपने कहा' : 'You said'}:
                                    </h4>
                                    <button
                                        onClick={() => setShowTranscription(!showTranscription)}
                                        className="ml-auto text-blue-600 hover:text-blue-800 text-sm"
                                    >
                                        Hide
                                    </button>
                                </div>
                                <p className="text-blue-700 dark:text-blue-300">{currentTranscription}</p>
                            </div>
                        )}

                        {/* AI Response */}
                        {currentResponse && (
                            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200">
                                <div className="flex items-center mb-2">
                                    <Bot className="w-4 h-4 text-green-600 mr-2" />
                                    <h4 className="font-medium text-green-800 dark:text-green-200">
                                        {culturalContext?.language?.startsWith('hi') ? 'MITRA कहता है' : 'MITRA says'}:
                                    </h4>
                                </div>
                                <p className="text-green-700 dark:text-green-300">{currentResponse}</p>
                            </div>
                        )}

                        {/* TTS Audio Player */}
                        {audioSource && (
                            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border">
                                <div className="flex items-center mb-3">
                                    <Volume2 className="w-4 h-4 text-gray-600 mr-2" />
                                    <h4 className="font-medium text-gray-700 dark:text-gray-300">
                                        Response Audio
                                    </h4>
                                </div>
                                <VoicePlayer
                                    ref={voicePlayerRef}
                                    src={audioSource}
                                    autoPlay={false}
                                    showControls={true}
                                    enableVolumeControl={true}
                                    enableSpeedControl={false}
                                    showProgress={true}
                                    allowInterruption={true}
                                    onPlayStart={handlePlaybackStart}
                                    onPlayEnd={handlePlaybackEnd}
                                    onError={handlePlaybackError}
                                />
                            </div>
                        )}
                    </div>
                )}

                {/* Emotion & Wellness Display */}
                {currentEmotion && emotionInfo && (
                    <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center">
                                <Heart className="w-4 h-4 text-pink-500 mr-2" />
                                <h4 className="font-medium text-gray-800 dark:text-gray-200">
                                    {culturalContext?.language?.startsWith('hi') ? 'मूड विश्लेषण' : 'Mood Analysis'}
                                </h4>
                            </div>
                            <button
                                onClick={() => setShowEmotionDetails(!showEmotionDetails)}
                                className="text-gray-600 hover:text-gray-800 text-sm"
                            >
                                {showEmotionDetails ? 'Less' : 'More'}
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-3 text-sm">
                            <div>
                                <span className="text-gray-600 dark:text-gray-400">
                                    {culturalContext?.language?.startsWith('hi') ? 'भावना' : 'Emotion'}: 
                                </span>
                                <span className="font-medium ml-2">
                                    {emotionInfo.emoji} {emotionInfo.text} ({emotionInfo.confidence}%)
                                </span>
                            </div>
                            
                            <div>
                                <span className="text-gray-600 dark:text-gray-400">
                                    {culturalContext?.language?.startsWith('hi') ? 'तनाव स्तर' : 'Stress Level'}: 
                                </span>
                                <span className="font-medium ml-2">
                                    {Math.round(emotionInfo.stressLevel * 100)}%
                                </span>
                            </div>
                        </div>
                        
                        {/* Crisis Level Indicator */}
                        {currentEmotion && (
                            <div className="mt-3">
                                <div className="text-xs text-gray-500 mb-1">
                                    {culturalContext?.language?.startsWith('hi') ? 'मानसिक स्वास्थ्य स्तर' : 'Mental Health Level'}
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div 
                                        className={`h-2 rounded-full transition-all ${
                                            emotionInfo.stressLevel >= crisisThreshold ? 'bg-red-500' :
                                            emotionInfo.stressLevel >= 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                                        }`}
                                        style={{ width: `${Math.min(emotionInfo.stressLevel * 100, 100)}%` }}
                                    />
                                </div>
                                {emotionInfo.stressLevel >= crisisThreshold && (
                                    <div className="mt-2 text-xs text-red-600">
                                        ⚠️ High stress detected - Support available
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Detailed Emotion Analysis */}
                        {showEmotionDetails && currentEmotion && (
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                                <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                                    <div>Voice Characteristics:</div>
                                    <div className="grid grid-cols-2 gap-2 ml-2">
                                        <div>Pitch: {Math.round(currentEmotion.characteristics.pitch)}%</div>
                                        <div>Volume: {Math.round(currentEmotion.characteristics.volume)}%</div>
                                        <div>Speed: {Math.round(currentEmotion.characteristics.speed)}%</div>
                                        <div>Clarity: {Math.round(currentEmotion.characteristics.clarity)}%</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Session Info */}
                {(conversationId || sessionId) && showAdvancedControls && (
                    <div className="text-center text-xs text-gray-500 dark:text-gray-400 space-y-1">
                        {conversationId && (
                            <p>
                                {culturalContext?.language?.startsWith('hi') ? 'बातचीत ID' : 'Conversation ID'}: 
                                {conversationId.substring(0, 8)}...
                            </p>
                        )}
                        <p>
                            {culturalContext?.language?.startsWith('hi') ? 'कुल संदेश' : 'Total Messages'}: 
                            {getConversationHistory().length}
                        </p>
                    </div>
                )}
            </div>

            {/* Emergency Contact (Crisis Support) */}
            <div className="p-4 bg-red-50 border-t border-red-200">
                <div className="flex items-center justify-center text-center">
                    <Phone className="w-4 h-4 text-red-500 mr-2" />
                    <span className="text-red-700 text-sm font-medium">
                        {culturalContext?.language?.startsWith('hi') 
                            ? 'तुरंत मदद: Tele MANAS 14416 (24/7 Crisis Support)'
                            : 'Immediate Help: Tele MANAS 14416 (24/7 Crisis Support)'
                        }
                    </span>
                </div>
            </div>

            {/* Instructions */}
            {!chatPaneMode && (
                <div className="p-4 bg-blue-50 text-center">
                    <div className="text-xs text-blue-600 space-y-1">
                        <p>
                            {culturalContext?.language?.startsWith('hi')
                                ? '🎤 माइक्रोफोन दबाकर रिकॉर्डिंग शुरू करें'
                                : '🎤 Press microphone to start recording'
                            }
                        </p>
                        <p>
                            {culturalContext?.language?.startsWith('hi')
                                ? '🛑 स्टॉप बटन दबाकर रिकॉर्डिंग बंद करें'
                                : '🛑 Press stop to end recording'
                            }
                        </p>
                        <p>
                            {culturalContext?.language?.startsWith('hi')
                                ? '🔊 जवाब अपने आप चलेगा'
                                : '🔊 Response will play automatically'
                            }
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VoiceCompanion;