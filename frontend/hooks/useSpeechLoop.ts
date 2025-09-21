/**
 * useSpeechLoop Hook - Complete Voice Interaction Workflow
 * 
 * This hook manages the entire file-based push-to-talk voice interaction
 * workflow for MITRA Sense mental health platform:
 * 
 * 1. Accept audio blobs from VoiceRecorder
 * 2. Upload to backend /api/v1/voice/pipeline/audio
 * 3. Process backend response (transcription, emotion, TTS)
 * 4. Play TTS audio with interruption handling
 * 5. Maintain conversation context for RAG + Gemini AI
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import {
    VoiceRecordingError,
    VoicePlaybackError,
    VoiceEmotionAnalysis,
    VoiceCulturalContext,
    AudioBlobWithMetadata
} from '../components/voice/types';

/**
 * Speech loop error types covering all workflow stages
 */
export type SpeechLoopError =
    | 'upload-failed'
    | 'network-error'
    | 'backend-processing-failed'
    | 'audio-playback-failed'
    | 'invalid-response'
    | 'timeout-error'
    | 'session-expired'
    | VoiceRecordingError
    | VoicePlaybackError;

/**
 * Speech loop states for the complete workflow
 */
export type SpeechLoopState =
    | 'idle'           // No active operation
    | 'recording'      // Currently recording audio
    | 'uploading'      // Uploading audio to backend
    | 'processing'     // Backend processing (STT, emotion, AI, TTS)
    | 'playing'        // Playing TTS response
    | 'error';         // Error state

/**
 * Backend API response structure for voice pipeline
 */
export interface VoicePipelineResponse {
    /** Transcribed text from user's audio */
    transcription: {
        text: string;
        language: string;
        confidence: number;
    };

    /** Emotion analysis results */
    emotion: VoiceEmotionAnalysis;

    /** AI-generated response */
    aiResponse: {
        text: string;
        crisisScore: number;
        culturalAdaptations: Record<string, string>;
        suggestedActions: string[];
        ragSources?: string[];
    };

    /** Text-to-speech audio */
    ttsAudio: {
        url?: string;           // Audio URL if hosted
        blob?: Blob;           // Audio blob if returned directly
        format: string;        // Audio format
        duration: number;      // Audio duration in seconds
    };

    /** Session and context information */
    session: {
        sessionId: string;
        conversationId: string;
        timestamp: string;
    };
}

/**
 * Configuration for the speech loop hook
 */
export interface UseSpeechLoopConfig {
    /** Backend API base URL */
    apiBaseUrl?: string;

    /** Authentication token for API calls */
    authToken?: string;

    /** Cultural context for voice interactions */
    culturalContext?: Partial<VoiceCulturalContext>;

    /** Initial conversation ID to maintain context with text chat */
    initialConversationId?: string;

    /** Maximum upload timeout in milliseconds */
    uploadTimeout?: number;

    /** Maximum processing timeout in milliseconds */
    processingTimeout?: number;

    /** Auto-play TTS responses */
    autoPlayResponses?: boolean;

    /** Enable conversation context persistence */
    enableContextPersistence?: boolean;

    /** Callback for successful interactions */
    onInteractionComplete?: (response: VoicePipelineResponse) => void;

    /** Callback for errors */
    onError?: (error: SpeechLoopError, message: string, details?: any) => void;

    /** Callback for state changes */
    onStateChange?: (state: SpeechLoopState) => void;
}

/**
 * Speech loop control functions and state
 */
export interface UseSpeechLoopReturn {
    // Current states
    state: SpeechLoopState;
    isRecording: boolean;
    isProcessing: boolean;
    isPlaying: boolean;
    error: { type: SpeechLoopError; message: string; details?: any } | null;

    // Current interaction data
    currentTranscription: string | null;
    currentResponse: string | null;
    currentEmotion: VoiceEmotionAnalysis | null;

    // Conversation context
    conversationId: string | null;
    sessionId: string | null;

    // Control functions
    startRecording: () => Promise<void>;
    stopRecording: () => void;
    playResponse: (audioUrl?: string) => Promise<void>;
    cancelCurrent: () => void;
    clearError: () => void;
    resetSession: () => void;

    // Audio handling
    processAudioBlob: (audioBlob: Blob, duration: number) => Promise<void>;

    // Conversation management
    getConversationHistory: () => VoicePipelineResponse[];
}

/**
 * Custom hook for managing complete voice interaction workflow
 */
export const useSpeechLoop = (config: UseSpeechLoopConfig = {}): UseSpeechLoopReturn => {
    const {
        apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api/v1',
        authToken,
        culturalContext,
        initialConversationId,
        uploadTimeout = parseInt(process.env.NEXT_PUBLIC_VOICE_UPLOAD_TIMEOUT || '30000'),
        processingTimeout = parseInt(process.env.NEXT_PUBLIC_VOICE_PROCESSING_TIMEOUT || '60000'),
        autoPlayResponses = true,
        enableContextPersistence = true,
        onInteractionComplete,
        onError,
        onStateChange,
    } = config;

    // State management
    const [state, setState] = useState<SpeechLoopState>('idle');
    const [error, setError] = useState<{ type: SpeechLoopError; message: string; details?: any } | null>(null);
    const [currentTranscription, setCurrentTranscription] = useState<string | null>(null);
    const [currentResponse, setCurrentResponse] = useState<string | null>(null);
    const [currentEmotion, setCurrentEmotion] = useState<VoiceEmotionAnalysis | null>(null);
    const [conversationId, setConversationId] = useState<string | null>(initialConversationId || null);
    const [sessionId, setSessionId] = useState<string | null>(null);

    // Refs for managing audio and requests
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);
    const conversationHistoryRef = useRef<VoicePipelineResponse[]>([]);

    // Computed states
    const isRecording = state === 'recording';
    const isProcessing = state === 'uploading' || state === 'processing';
    const isPlaying = state === 'playing';

    /**
     * Update state and notify listeners
     */
    const updateState = useCallback((newState: SpeechLoopState) => {
        setState(newState);
        onStateChange?.(newState);
    }, [onStateChange]);

    /**
     * Handle errors with proper cleanup
     */
    const handleError = useCallback((errorType: SpeechLoopError, message: string, details?: any) => {
        console.error('Speech loop error:', { errorType, message, details });

        const errorObj = { type: errorType, message, details };
        setError(errorObj);
        updateState('error');

        // Cleanup on error
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }

        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }

        onError?.(errorType, message, details);
    }, [updateState, onError]);

    /**
     * Clear current error state
     */
    const clearError = useCallback(() => {
        setError(null);
        if (state === 'error') {
            updateState('idle');
        }
    }, [state, updateState]);

    /**
     * Generate or retrieve session ID
     */
    const ensureSessionId = useCallback((): string => {
        if (sessionId) return sessionId;

        const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        return newSessionId;
    }, [sessionId]);

    /**
     * Upload audio blob to backend voice pipeline
     */
    const uploadAudioToBackend = useCallback(async (audioBlob: Blob, duration: number): Promise<VoicePipelineResponse> => {
        const currentSessionId = ensureSessionId();

        // Create FormData for audio upload
        const formData = new FormData();
        formData.append('audio', audioBlob, 'voice-recording.webm');
        formData.append('duration', duration.toString());
        formData.append('sessionId', currentSessionId);

        if (conversationId) {
            formData.append('conversationId', conversationId);
        }

        if (culturalContext) {
            formData.append('culturalContext', JSON.stringify(culturalContext));
        }

        // Debug log for conversation context
        if (process.env.NEXT_PUBLIC_DEBUG_MODE === 'true') {
            console.log('Voice context info:', {
                conversationId: conversationId || 'None - will create new',
                sessionId: currentSessionId,
                hasContext: !!conversationId
            });
        }

        // Setup abort controller for request cancellation
        abortControllerRef.current = new AbortController();

        const requestConfig: RequestInit = {
            method: 'POST',
            body: formData,
            signal: abortControllerRef.current.signal,
            headers: {
                // Don't set Content-Type - let browser set it for FormData
                ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
            },
        };

        // Add timeout handling
        const timeoutId = setTimeout(() => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        }, uploadTimeout + processingTimeout);

        try {
            // Log API call for debugging
            if (process.env.NEXT_PUBLIC_DEBUG_MODE === 'true') {
                console.log('Voice API call:', {
                    url: `${apiBaseUrl}/voice/pipeline/audio`,
                    audioSize: audioBlob.size,
                    audioType: audioBlob.type,
                    culturalContext,
                    conversationId,
                });
            }

            const response = await fetch(`${apiBaseUrl}/voice/pipeline/audio`, requestConfig);

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorText = await response.text();
                const errorMessage = `Backend error (${response.status}): ${errorText}`;

                // Provide specific error guidance
                if (response.status === 404) {
                    throw new Error(`Voice API endpoint not found. Make sure the FastAPI backend is running on port 8000. ${errorMessage}`);
                } else if (response.status >= 500) {
                    throw new Error(`Backend server error. Check backend logs. ${errorMessage}`);
                } else {
                    throw new Error(errorMessage);
                }
            }

            const result: VoicePipelineResponse = await response.json();

            // Log successful response for debugging
            if (process.env.NEXT_PUBLIC_DEBUG_MODE === 'true') {
                console.log('Voice API response:', {
                    transcription: result.transcription?.text,
                    responseText: result.aiResponse?.text,
                    emotion: result.emotion,
                    crisisScore: result.aiResponse?.crisisScore,
                });
            }

            // Update conversation context
            if (result.session?.conversationId) {
                setConversationId(result.session.conversationId);
            }

            return result;

        } catch (error) {
            clearTimeout(timeoutId);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Voice request was cancelled (timeout or user interruption)');
                }

                // Network error handling
                if (error.message.includes('fetch')) {
                    throw new Error('Network connection failed. Make sure the backend is running and accessible.');
                }

                throw error;
            }
            throw new Error('Unknown voice processing error');
        } finally {
            abortControllerRef.current = null;
        }
    }, [apiBaseUrl, authToken, culturalContext, conversationId, uploadTimeout, processingTimeout, ensureSessionId]);

    /**
     * Play TTS audio with interruption handling
     */
    const playTTSAudio = useCallback(async (audioSource: string | Blob): Promise<void> => {
        return new Promise((resolve, reject) => {
            try {
                // Stop any currently playing audio
                if (audioRef.current) {
                    audioRef.current.pause();
                    audioRef.current = null;
                }

                // Create new audio element
                const audio = new Audio();
                audioRef.current = audio;

                // Set up event handlers
                audio.onended = () => {
                    updateState('idle');
                    audioRef.current = null;
                    resolve();
                };

                audio.onerror = (e) => {
                    audioRef.current = null;
                    reject(new Error('Audio playback failed'));
                };

                audio.oncanplaythrough = () => {
                    updateState('playing');
                    audio.play().catch(reject);
                };

                // Set audio source
                if (audioSource instanceof Blob) {
                    const audioUrl = URL.createObjectURL(audioSource);
                    audio.src = audioUrl;

                    // Cleanup URL when done
                    audio.onended = () => {
                        URL.revokeObjectURL(audioUrl);
                        updateState('idle');
                        audioRef.current = null;
                        resolve();
                    };
                } else {
                    audio.src = audioSource;
                }

                // Load the audio
                audio.load();

            } catch (error) {
                audioRef.current = null;
                reject(error);
            }
        });
    }, [updateState]);

    /**
     * Process audio blob through complete voice pipeline
     */
    const processAudioBlob = useCallback(async (audioBlob: Blob, duration: number): Promise<void> => {
        try {
            clearError();
            updateState('uploading');

            // Upload audio and get AI response
            const response = await uploadAudioToBackend(audioBlob, duration);

            updateState('processing');

            // Update current interaction data
            setCurrentTranscription(response.transcription.text);
            setCurrentResponse(response.aiResponse.text);
            setCurrentEmotion(response.emotion);

            // Add to conversation history
            if (enableContextPersistence) {
                conversationHistoryRef.current.push(response);
            }

            // Call completion callback
            onInteractionComplete?.(response);

            // Auto-play TTS response if enabled
            if (autoPlayResponses && (response.ttsAudio.url || response.ttsAudio.blob)) {
                const audioSource = response.ttsAudio.blob || response.ttsAudio.url!;
                await playTTSAudio(audioSource);
            } else {
                updateState('idle');
            }

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown processing error';

            if (errorMessage.includes('cancelled')) {
                updateState('idle');
            } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
                handleError('network-error', 'Network connection failed', error);
            } else if (errorMessage.includes('Backend error')) {
                handleError('backend-processing-failed', errorMessage, error);
            } else {
                handleError('upload-failed', errorMessage, error);
            }
        }
    }, [
        clearError,
        updateState,
        uploadAudioToBackend,
        enableContextPersistence,
        onInteractionComplete,
        autoPlayResponses,
        playTTSAudio,
        handleError
    ]);

    /**
     * Start recording (to be connected to VoiceRecorder)
     */
    const startRecording = useCallback(async (): Promise<void> => {
        try {
            clearError();

            // Stop any currently playing audio
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }

            updateState('recording');
        } catch (error) {
            handleError('recording-failed', 'Failed to start recording', error);
        }
    }, [clearError, updateState, handleError]);

    /**
     * Stop recording
     */
    const stopRecording = useCallback(() => {
        if (state === 'recording') {
            updateState('idle');
        }
    }, [state, updateState]);

    /**
     * Play a specific audio response
     */
    const playResponse = useCallback(async (audioUrl?: string): Promise<void> => {
        if (!audioUrl) {
            handleError('audio-playback-failed', 'No audio URL provided');
            return;
        }

        try {
            await playTTSAudio(audioUrl);
        } catch (error) {
            handleError('audio-playback-failed', 'Failed to play audio response', error);
        }
    }, [playTTSAudio, handleError]);

    /**
     * Cancel current operation
     */
    const cancelCurrent = useCallback(() => {
        // Abort any pending requests
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }

        // Stop audio playback
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }

        updateState('idle');
    }, [updateState]);

    /**
     * Reset session and conversation context
     */
    const resetSession = useCallback(() => {
        cancelCurrent();
        setSessionId(null);
        setConversationId(null);
        setCurrentTranscription(null);
        setCurrentResponse(null);
        setCurrentEmotion(null);
        conversationHistoryRef.current = [];
        clearError();
    }, [cancelCurrent, clearError]);

    /**
     * Get conversation history
     */
    const getConversationHistory = useCallback((): VoicePipelineResponse[] => {
        return [...conversationHistoryRef.current];
    }, []);

    /**
     * Cleanup on unmount
     */
    useEffect(() => {
        return () => {
            // Cleanup audio
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }

            // Abort pending requests
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    return {
        // States
        state,
        isRecording,
        isProcessing,
        isPlaying,
        error,

        // Current interaction data
        currentTranscription,
        currentResponse,
        currentEmotion,

        // Session context
        conversationId,
        sessionId,

        // Control functions
        startRecording,
        stopRecording,
        playResponse,
        cancelCurrent,
        clearError,
        resetSession,

        // Audio processing
        processAudioBlob,

        // Conversation management
        getConversationHistory,
    };
};

export default useSpeechLoop;