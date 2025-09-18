/**
 * TypeScript type definitions for Voice Recording functionality
 * Used across voice-related components in MITRA Sense
 */

/**
 * Audio recording states
 */
export type RecordingState = 'idle' | 'recording' | 'processing' | 'error';

/**
 * Audio playback states
 */
export type PlaybackState = 'idle' | 'playing' | 'paused' | 'loading' | 'error';

/**
 * Voice recording error types
 */
export type VoiceRecordingError =
    | 'permission-denied'
    | 'device-not-found'
    | 'browser-not-supported'
    | 'recording-failed'
    | 'duration-exceeded'
    | 'file-too-large'
    | 'invalid-format';

/**
 * Voice playback error types
 */
export type VoicePlaybackError =
    | 'audio-load-failed'
    | 'playback-failed'
    | 'invalid-audio-data'
    | 'browser-not-supported';

/**
 * Supported audio formats for recording
 */
export type AudioFormat =
    | 'audio/webm'
    | 'audio/webm;codecs=opus'
    | 'audio/mp4'
    | 'audio/ogg;codecs=opus'
    | 'audio/wav';

/**
 * Audio quality presets
 */
export type AudioQuality = 'low' | 'medium' | 'high';

/**
 * Language codes supported for voice processing
 */
export type VoiceLanguageCode =
    | 'en-US'   // English (US)
    | 'en-IN'   // English (India)
    | 'hi-IN'   // Hindi (India)
    | 'ta-IN'   // Tamil (India)
    | 'te-IN'   // Telugu (India)
    | 'bn-IN'   // Bengali (India)
    | 'gu-IN'   // Gujarati (India)
    | 'kn-IN'   // Kannada (India)
    | 'ml-IN'   // Malayalam (India)
    | 'mr-IN'   // Marathi (India)
    | 'pa-IN'   // Punjabi (India)
    | 'ur-IN';  // Urdu (India)

/**
 * Emotion detection results from voice analysis
 */
export interface VoiceEmotionAnalysis {
    /** Primary detected emotion */
    primaryEmotion: string;
    /** Confidence score for primary emotion (0-1) */
    confidence: number;
    /** All detected emotions with scores */
    emotions: Record<string, number>;
    /** Stress level indicator (0-1) */
    stressLevel: number;
    /** Voice characteristics */
    characteristics: {
        pitch: number;
        volume: number;
        speed: number;
        clarity: number;
    };
}

/**
 * Cultural context for voice interactions
 */
export interface VoiceCulturalContext {
    /** Detected or selected language */
    language: VoiceLanguageCode;
    /** Regional dialect if detected */
    dialect?: string;
    /** Cultural greeting style preference */
    greetingStyle: 'formal' | 'informal' | 'traditional';
    /** Family context awareness */
    familyContext: 'individual' | 'family-aware' | 'elder-present';
}

/**
 * Voice recording configuration
 */
export interface VoiceRecordingConfig {
    /** Maximum recording duration in seconds */
    maxDuration: number;
    /** Audio quality preset */
    quality: AudioQuality;
    /** Preferred audio format */
    format: AudioFormat;
    /** Enable noise suppression */
    noiseSuppression: boolean;
    /** Enable echo cancellation */
    echoCancellation: boolean;
    /** Enable automatic gain control */
    autoGainControl: boolean;
}

/**
 * Audio blob with metadata
 */
export interface AudioBlobWithMetadata {
    /** The actual audio blob */
    blob: Blob;
    /** Recording duration in seconds */
    duration: number;
    /** Audio format/MIME type */
    format: string;
    /** File size in bytes */
    size: number;
    /** Timestamp when recording was created */
    timestamp: Date;
    /** Audio quality information */
    quality: {
        bitrate?: number;
        sampleRate?: number;
        channels?: number;
    };
}

/**
 * Voice interaction session data
 */
export interface VoiceSession {
    /** Unique session identifier */
    sessionId: string;
    /** Session start timestamp */
    startTime: Date;
    /** Session end timestamp */
    endTime?: Date;
    /** Total recordings in session */
    recordingCount: number;
    /** Total session duration */
    totalDuration: number;
    /** Detected languages used */
    languages: VoiceLanguageCode[];
    /** Cultural context for session */
    culturalContext: VoiceCulturalContext;
    /** Crisis indicators detected */
    crisisIndicators: string[];
    /** Overall emotion analysis for session */
    emotionSummary?: VoiceEmotionAnalysis;
}

/**
 * Voice component props for recording
 */
export interface VoiceRecorderProps {
    /** Callback when recording is completed successfully */
    onRecordingComplete: (audioData: AudioBlobWithMetadata) => void;
    /** Callback when an error occurs */
    onError: (error: VoiceRecordingError, message: string) => void;
    /** Recording configuration */
    config?: Partial<VoiceRecordingConfig>;
    /** Custom CSS classes */
    className?: string;
    /** Disabled state */
    disabled?: boolean;
    /** Cultural context for the recording */
    culturalContext?: Partial<VoiceCulturalContext>;
}

/**
 * Voice component props for playback
 */
export interface VoicePlayerProps {
    /** Audio source (blob, URL, or base64) */
    audioSource: Blob | string;
    /** Auto-play when audio is loaded */
    autoPlay?: boolean;
    /** Show playback controls */
    showControls?: boolean;
    /** Callback when playback starts */
    onPlaybackStart?: () => void;
    /** Callback when playback ends */
    onPlaybackEnd?: () => void;
    /** Callback when playback is paused */
    onPlaybackPause?: () => void;
    /** Callback when an error occurs */
    onError?: (error: VoicePlaybackError, message: string) => void;
    /** Custom CSS classes */
    className?: string;
    /** Allow interruption by other audio */
    allowInterruption?: boolean;
}

/**
 * Voice settings/preferences
 */
export interface VoiceSettings {
    /** Default language for voice interactions */
    defaultLanguage: VoiceLanguageCode;
    /** Recording quality preference */
    recordingQuality: AudioQuality;
    /** Auto-detect language from speech */
    autoDetectLanguage: boolean;
    /** Cultural context preferences */
    culturalPreferences: VoiceCulturalContext;
    /** Accessibility settings */
    accessibility: {
        /** Show visual feedback for audio */
        visualFeedback: boolean;
        /** Show captions/transcripts */
        showCaptions: boolean;
        /** High contrast mode */
        highContrast: boolean;
        /** Reduced motion */
        reducedMotion: boolean;
    };
    /** Privacy settings */
    privacy: {
        /** Allow emotion analysis */
        allowEmotionAnalysis: boolean;
        /** Store voice recordings locally */
        storeRecordings: boolean;
        /** Share data for improvement */
        shareForImprovement: boolean;
    };
}

/**
 * Voice analytics data
 */
export interface VoiceAnalytics {
    /** Total voice interactions */
    totalInteractions: number;
    /** Average session duration */
    averageSessionDuration: number;
    /** Most used language */
    primaryLanguage: VoiceLanguageCode;
    /** Emotion trends over time */
    emotionTrends: Array<{
        date: Date;
        emotions: Record<string, number>;
    }>;
    /** Crisis detection frequency */
    crisisDetectionCount: number;
    /** Success rate of voice interactions */
    successRate: number;
}

/**
 * Constants for voice functionality
 */
export const VOICE_CONSTANTS = {
    /** Default recording configuration */
    DEFAULT_RECORDING_CONFIG: {
        maxDuration: 180, // 3 minutes
        quality: 'medium' as AudioQuality,
        format: 'audio/webm;codecs=opus' as AudioFormat,
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true,
    },

    /** Audio quality settings */
    QUALITY_SETTINGS: {
        low: { bitrate: 64000, sampleRate: 22050 },
        medium: { bitrate: 128000, sampleRate: 44100 },
        high: { bitrate: 256000, sampleRate: 48000 },
    },

    /** File size limits (in bytes) */
    MAX_FILE_SIZE: {
        low: 5 * 1024 * 1024,    // 5 MB
        medium: 10 * 1024 * 1024, // 10 MB
        high: 20 * 1024 * 1024,   // 20 MB
    },

    /** Supported MIME types in order of preference */
    SUPPORTED_MIME_TYPES: [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus',
        'audio/wav',
    ] as AudioFormat[],
} as const;