'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Square, Clock, AlertCircle } from 'lucide-react';

/**
 * Recording states for the VoiceRecorder component
 */
export type RecordingState = 'idle' | 'recording' | 'processing' | 'error';

/**
 * Error types that can occur during voice recording
 */
export type VoiceRecordingError =
    | 'permission-denied'
    | 'device-not-found'
    | 'browser-not-supported'
    | 'recording-failed'
    | 'duration-exceeded';

/**
 * Props interface for the VoiceRecorder component
 */
export interface VoiceRecorderProps {
    /** Callback when recording is completed successfully */
    onRecordingComplete: (audioBlob: Blob, duration: number) => void;
    /** Callback when an error occurs */
    onError: (error: VoiceRecordingError, message: string) => void;
    /** Maximum recording duration in seconds (default: 180 = 3 minutes) */
    maxDuration?: number;
    /** Audio format for recording (default: 'audio/webm') */
    audioFormat?: string;
    /** Custom CSS classes for styling */
    className?: string;
    /** Disabled state */
    disabled?: boolean;
}

/**
 * Configuration for MediaRecorder options
 */
const RECORDER_OPTIONS = {
    audioBitsPerSecond: 128000, // 128 kbps for good quality
    mimeType: 'audio/webm;codecs=opus', // Fallback will be handled
};

/**
 * VoiceRecorder Component
 * 
 * A comprehensive push-to-talk voice recording component with:
 * - MediaRecorder API integration
 * - Microphone permission handling
 * - Recording duration limits
 * - Visual state indicators
 * - Error handling and recovery
 * - Accessibility features
 * 
 * @param props - VoiceRecorderProps
 * @returns JSX.Element
 */
export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
    onRecordingComplete,
    onError,
    maxDuration = 180, // 3 minutes default
    audioFormat = 'audio/webm',
    className = '',
    disabled = false,
}) => {
    // State management
    const [recordingState, setRecordingState] = useState<RecordingState>('idle');
    const [recordingDuration, setRecordingDuration] = useState<number>(0);
    const [errorMessage, setErrorMessage] = useState<string>('');

    // Refs for MediaRecorder and related functionality
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const streamRef = useRef<MediaStream | null>(null);
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const startTimeRef = useRef<number>(0);

    /**
     * Check if MediaRecorder is supported in the current browser
     */
    const isMediaRecorderSupported = useCallback((): boolean => {
        return typeof MediaRecorder !== 'undefined' &&
            typeof navigator.mediaDevices !== 'undefined' &&
            typeof navigator.mediaDevices.getUserMedia !== 'undefined';
    }, []);

    /**
     * Get the best supported audio MIME type for recording
     */
    const getSupportedMimeType = useCallback((): string => {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/ogg;codecs=opus',
            'audio/wav'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }

        return 'audio/webm'; // Fallback
    }, []);

    /**
     * Start the recording timer
     */
    const startTimer = useCallback(() => {
        startTimeRef.current = Date.now();
        timerRef.current = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
            setRecordingDuration(elapsed);

            // Auto-stop recording when max duration is reached
            if (elapsed >= maxDuration) {
                stopRecording();
            }
        }, 1000);
    }, [maxDuration]);

    /**
     * Stop the recording timer
     */
    const stopTimer = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, []);

    /**
     * Clean up media stream and recorder
     */
    const cleanup = useCallback(() => {
        // Stop timer
        stopTimer();

        // Stop media stream tracks
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        // Reset MediaRecorder
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current = null;
        }

        // Reset duration
        setRecordingDuration(0);
    }, [stopTimer]);

    /**
     * Request microphone permission and start recording
     */
    const startRecording = useCallback(async () => {
        try {
            // Check browser support
            if (!isMediaRecorderSupported()) {
                onError('browser-not-supported', 'Your browser does not support audio recording');
                return;
            }

            setRecordingState('processing');
            setErrorMessage('');

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                }
            });

            streamRef.current = stream;

            // Create MediaRecorder with best supported format
            const mimeType = getSupportedMimeType();
            const options = { ...RECORDER_OPTIONS, mimeType };

            const mediaRecorder = new MediaRecorder(stream, options);
            mediaRecorderRef.current = mediaRecorder;

            // Reset audio chunks
            audioChunksRef.current = [];

            // Set up event handlers
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
                const duration = recordingDuration;

                // Cleanup first
                cleanup();

                // Set state to processing
                setRecordingState('processing');

                // Call completion callback
                setTimeout(() => {
                    onRecordingComplete(audioBlob, duration);
                    setRecordingState('idle');
                }, 100);
            };

            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event);
                cleanup();
                setRecordingState('error');
                onError('recording-failed', 'Failed to record audio');
            };

            // Start recording
            mediaRecorder.start();
            setRecordingState('recording');
            startTimer();

        } catch (error) {
            console.error('Error starting recording:', error);
            cleanup();
            setRecordingState('error');

            if (error instanceof Error) {
                if (error.name === 'NotAllowedError') {
                    onError('permission-denied', 'Microphone permission was denied');
                } else if (error.name === 'NotFoundError') {
                    onError('device-not-found', 'No microphone found');
                } else {
                    onError('recording-failed', error.message);
                }
            } else {
                onError('recording-failed', 'An unknown error occurred');
            }
        }
    }, [
        isMediaRecorderSupported,
        getSupportedMimeType,
        onError,
        onRecordingComplete,
        startTimer,
        cleanup,
        recordingDuration
    ]);

    /**
     * Stop the current recording
     */
    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && recordingState === 'recording') {
            mediaRecorderRef.current.stop();
        }
    }, [recordingState]);

    /**
     * Toggle recording state (start/stop)
     */
    const toggleRecording = useCallback(() => {
        if (disabled) return;

        if (recordingState === 'idle') {
            startRecording();
        } else if (recordingState === 'recording') {
            stopRecording();
        }
    }, [recordingState, disabled, startRecording, stopRecording]);

    /**
     * Format duration in MM:SS format
     */
    const formatDuration = useCallback((seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, []);

    /**
     * Cleanup on component unmount
     */
    useEffect(() => {
        return () => {
            cleanup();
        };
    }, [cleanup]);

    /**
     * Get button styling based on current state
     */
    const getButtonStyling = () => {
        const baseClasses = 'relative flex items-center justify-center w-16 h-16 rounded-full transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-opacity-75 disabled:opacity-50 disabled:cursor-not-allowed';

        switch (recordingState) {
            case 'recording':
                return `${baseClasses} bg-red-500 hover:bg-red-600 text-white focus:ring-red-300 animate-pulse`;
            case 'processing':
                return `${baseClasses} bg-yellow-500 text-white cursor-not-allowed`;
            case 'error':
                return `${baseClasses} bg-red-600 text-white`;
            default:
                return `${baseClasses} bg-blue-500 hover:bg-blue-600 text-white focus:ring-blue-300`;
        }
    };

    /**
     * Get the appropriate icon for current state
     */
    const getButtonIcon = () => {
        switch (recordingState) {
            case 'recording':
                return <Square size={24} />;
            case 'processing':
                return <Clock size={24} className="animate-spin" />;
            case 'error':
                return <AlertCircle size={24} />;
            default:
                return <Mic size={24} />;
        }
    };

    /**
     * Get status text for accessibility and user feedback
     */
    const getStatusText = () => {
        switch (recordingState) {
            case 'recording':
                return `Recording... ${formatDuration(recordingDuration)}`;
            case 'processing':
                return 'Processing audio...';
            case 'error':
                return errorMessage || 'Recording error';
            default:
                return 'Click to start recording';
        }
    };

    return (
        <div className={`voice-recorder flex flex-col items-center space-y-4 ${className}`}>
            {/* Main Recording Button */}
            <button
                onClick={toggleRecording}
                disabled={disabled || recordingState === 'processing'}
                className={getButtonStyling()}
                aria-label={getStatusText()}
                type="button"
            >
                {getButtonIcon()}

                {/* Recording indicator ring */}
                {recordingState === 'recording' && (
                    <div className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping" />
                )}
            </button>

            {/* Status Display */}
            <div className="text-center">
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {getStatusText()}
                </div>

                {/* Duration and limit display */}
                {recordingState === 'recording' && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Max: {formatDuration(maxDuration)}
                    </div>
                )}

                {/* Error message */}
                {recordingState === 'error' && errorMessage && (
                    <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                        {errorMessage}
                    </div>
                )}
            </div>

            {/* Recording Progress Bar */}
            {recordingState === 'recording' && (
                <div className="w-full max-w-xs">
                    <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                        <div
                            className="bg-red-500 h-2 rounded-full transition-all duration-1000"
                            style={{ width: `${(recordingDuration / maxDuration) * 100}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Instructions */}
            {recordingState === 'idle' && (
                <div className="text-xs text-gray-500 dark:text-gray-400 text-center max-w-xs">
                    Press and hold to record up to {Math.floor(maxDuration / 60)} minutes
                </div>
            )}
        </div>
    );
};

export default VoiceRecorder;