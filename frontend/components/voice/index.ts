/**
 * Voice Components Export Index
 * 
 * This file provides a centralized export point for all voice-related components
 * and utilities in the MITRA Sense application.
 */

// Main components
export { default as VoiceRecorder } from './VoiceRecorder';
export type { VoiceRecorderProps } from './VoiceRecorder';

export { default as VoicePlayer } from './VoicePlayer';
export type { VoicePlayerProps, VoicePlayerRef, PlaybackSpeed } from './VoicePlayer';

export { default as VoiceCompanion } from './VoiceCompanion';
export type { VoiceCompanionProps } from './VoiceCompanion';

// Demo component (for development/testing)
export { default as VoiceRecorderDemo } from './VoiceRecorderDemo';
export { default as VoicePlayerDemo } from './VoicePlayerDemo';
export { default as VoiceCompanionDemo } from './VoiceCompanionDemo';

// Type definitions
export type {
    RecordingState,
    PlaybackState,
    VoiceRecordingError,
    VoicePlaybackError,
    AudioFormat,
    AudioQuality,
    VoiceLanguageCode,
    VoiceEmotionAnalysis,
    VoiceCulturalContext,
    VoiceRecordingConfig,
    AudioBlobWithMetadata,
    VoiceSession,
    VoiceSettings,
    VoiceAnalytics,
} from './types';

// Constants
export { VOICE_CONSTANTS } from './types';

// Re-export commonly used types for convenience
export type {
    VoiceRecorderProps as RecorderProps,
    VoicePlayerProps as PlayerProps,
    AudioBlobWithMetadata as AudioBlob,
} from './types';