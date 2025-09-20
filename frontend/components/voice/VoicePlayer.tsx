'use client';

import React, { useState, useRef, useCallback, useEffect, useImperativeHandle, forwardRef } from 'react';
import {
    Play,
    Pause,
    Square,
    Volume2,
    VolumeX,
    Volume1,
    SkipBack,
    SkipForward,
    Loader2,
    AlertCircle
} from 'lucide-react';
import { PlaybackState, VoicePlaybackError } from './types';

/**
 * Audio playback speed options
 */
export type PlaybackSpeed = 0.5 | 0.75 | 1.0 | 1.25 | 1.5 | 2.0;

/**
 * Volume levels for accessibility
 */
export type VolumeLevel = 'muted' | 'low' | 'medium' | 'high';

/**
 * Props interface for VoicePlayer component
 */
export interface VoicePlayerProps {
    /** Audio source - can be a Blob URL, HTTP URL, or Blob object */
    src: string | Blob | null;

    /** Auto-play when audio source is provided */
    autoPlay?: boolean;

    /** Show detailed playback controls */
    showControls?: boolean;

    /** Enable volume control */
    enableVolumeControl?: boolean;

    /** Enable playback speed control */
    enableSpeedControl?: boolean;

    /** Show progress bar with seeking capability */
    showProgress?: boolean;

    /** Initial volume (0-1) */
    initialVolume?: number;

    /** Initial playback speed */
    initialSpeed?: PlaybackSpeed;

    /** Allow interruption by external events */
    allowInterruption?: boolean;

    /** Custom CSS classes */
    className?: string;

    /** Disabled state */
    disabled?: boolean;

    // Event callbacks
    /** Called when playback starts */
    onPlayStart?: () => void;

    /** Called when playback is paused */
    onPlayPause?: () => void;

    /** Called when playback stops */
    onPlayStop?: () => void;

    /** Called when playback ends naturally */
    onPlayEnd?: () => void;

    /** Called when an error occurs */
    onError?: (error: VoicePlaybackError, message: string) => void;

    /** Called when playback progress changes */
    onProgress?: (currentTime: number, duration: number, percentage: number) => void;

    /** Called when volume changes */
    onVolumeChange?: (volume: number, isMuted: boolean) => void;

    /** Called when playback speed changes */
    onSpeedChange?: (speed: PlaybackSpeed) => void;
}

/**
 * Ref interface for external control of VoicePlayer
 */
export interface VoicePlayerRef {
    play: () => Promise<void>;
    pause: () => void;
    stop: () => void;
    seekTo: (timeInSeconds: number) => void;
    setVolume: (volume: number) => void;
    setSpeed: (speed: PlaybackSpeed) => void;
    getCurrentTime: () => number;
    getDuration: () => number;
    getState: () => PlaybackState;
}

/**
 * VoicePlayer Component
 * 
 * A comprehensive audio player component for MITRA Sense with:
 * - Complete playback controls (play, pause, stop)
 * - Progress visualization with seeking
 * - Volume and speed controls
 * - Interruption handling
 * - Accessibility features
 * - Event callbacks for integration
 * - Memory management and cleanup
 * 
 * @param props - VoicePlayerProps
 * @param ref - VoicePlayerRef for external control
 * @returns JSX.Element
 */
export const VoicePlayer = forwardRef<VoicePlayerRef, VoicePlayerProps>(({
    src,
    autoPlay = false,
    showControls = true,
    enableVolumeControl = true,
    enableSpeedControl = false,
    showProgress = true,
    initialVolume = 0.8,
    initialSpeed = 1.0,
    allowInterruption = true,
    className = '',
    disabled = false,
    onPlayStart,
    onPlayPause,
    onPlayStop,
    onPlayEnd,
    onError,
    onProgress,
    onVolumeChange,
    onSpeedChange,
}, ref) => {
    // State management
    const [playbackState, setPlaybackState] = useState<PlaybackState>('idle');
    const [currentTime, setCurrentTime] = useState<number>(0);
    const [duration, setDuration] = useState<number>(0);
    const [volume, setVolumeState] = useState<number>(initialVolume);
    const [isMuted, setIsMuted] = useState<boolean>(false);
    const [speed, setSpeedState] = useState<PlaybackSpeed>(initialSpeed);
    const [error, setError] = useState<string>('');

    // Refs for audio management
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const progressUpdateRef = useRef<NodeJS.Timeout | null>(null);
    const audioUrlRef = useRef<string | null>(null);

    /**
     * Create audio URL from Blob if needed
     */
    const createAudioUrl = useCallback((source: string | Blob): string => {
        if (typeof source === 'string') {
            return source;
        }

        // Clean up previous URL
        if (audioUrlRef.current) {
            URL.revokeObjectURL(audioUrlRef.current);
        }

        // Create new URL
        const url = URL.createObjectURL(source);
        audioUrlRef.current = url;
        return url;
    }, []);

    /**
     * Handle audio errors with proper error types
     */
    const handleError = useCallback((errorType: VoicePlaybackError, message: string) => {
        console.error('VoicePlayer error:', { errorType, message });
        setError(message);
        setPlaybackState('error');
        onError?.(errorType, message);
    }, [onError]);

    /**
     * Clear error state
     */
    const clearError = useCallback(() => {
        setError('');
        if (playbackState === 'error') {
            setPlaybackState('idle');
        }
    }, [playbackState]);

    /**
     * Update progress and fire progress callback
     */
    const updateProgress = useCallback(() => {
        if (!audioRef.current) return;

        const current = audioRef.current.currentTime;
        const total = audioRef.current.duration;

        setCurrentTime(current);

        if (total && !isNaN(total)) {
            setDuration(total);
            const percentage = (current / total) * 100;
            onProgress?.(current, total, percentage);
        }
    }, [onProgress]);

    /**
     * Start progress updates
     */
    const startProgressUpdates = useCallback(() => {
        if (progressUpdateRef.current) {
            clearInterval(progressUpdateRef.current);
        }

        progressUpdateRef.current = setInterval(updateProgress, 100); // Update every 100ms
    }, [updateProgress]);

    /**
     * Stop progress updates
     */
    const stopProgressUpdates = useCallback(() => {
        if (progressUpdateRef.current) {
            clearInterval(progressUpdateRef.current);
            progressUpdateRef.current = null;
        }
    }, []);

    /**
     * Initialize audio element with source
     */
    const initializeAudio = useCallback(async (source: string | Blob) => {
        try {
            clearError();
            setPlaybackState('loading');

            // Create audio element
            const audio = new Audio();
            audioRef.current = audio;

            // Set up event listeners
            audio.onloadedmetadata = () => {
                setDuration(audio.duration);
                setPlaybackState('idle');
            };

            audio.oncanplaythrough = () => {
                if (autoPlay && !disabled) {
                    play();
                }
            };

            audio.onplay = () => {
                setPlaybackState('playing');
                startProgressUpdates();
                onPlayStart?.();
            };

            audio.onpause = () => {
                setPlaybackState('paused');
                stopProgressUpdates();
                onPlayPause?.();
            };

            audio.onended = () => {
                setPlaybackState('idle');
                stopProgressUpdates();
                setCurrentTime(0);
                onPlayEnd?.();
            };

            audio.onerror = () => {
                handleError('audio-load-failed', 'Failed to load audio file');
            };

            audio.ontimeupdate = updateProgress;

            // Set audio properties
            audio.volume = isMuted ? 0 : volume;
            audio.playbackRate = speed;
            audio.preload = 'metadata';

            // Set source
            const audioUrl = createAudioUrl(source);
            audio.src = audioUrl;

            // Load the audio
            audio.load();

        } catch (error) {
            handleError('audio-load-failed', error instanceof Error ? error.message : 'Unknown audio error');
        }
    }, [autoPlay, disabled, volume, isMuted, speed, onPlayStart, onPlayPause, onPlayEnd, handleError, updateProgress, startProgressUpdates, stopProgressUpdates, clearError, createAudioUrl]);

    /**
     * Cleanup audio resources
     */
    const cleanup = useCallback(() => {
        // Stop progress updates
        stopProgressUpdates();

        // Clean up audio element
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.src = '';
            audioRef.current = null;
        }

        // Clean up blob URL
        if (audioUrlRef.current) {
            URL.revokeObjectURL(audioUrlRef.current);
            audioUrlRef.current = null;
        }

        // Reset state
        setPlaybackState('idle');
        setCurrentTime(0);
        setDuration(0);
    }, [stopProgressUpdates]);

    /**
     * Play audio
     */
    const play = useCallback(async (): Promise<void> => {
        if (!audioRef.current || disabled) return;

        try {
            clearError();
            await audioRef.current.play();
        } catch (error) {
            handleError('playback-failed', error instanceof Error ? error.message : 'Playback failed');
        }
    }, [disabled, clearError, handleError]);

    /**
     * Pause audio
     */
    const pause = useCallback(() => {
        if (!audioRef.current) return;
        audioRef.current.pause();
    }, []);

    /**
     * Stop audio (pause and reset to beginning)
     */
    const stop = useCallback(() => {
        if (!audioRef.current) return;

        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setCurrentTime(0);
        setPlaybackState('idle');
        stopProgressUpdates();
        onPlayStop?.();
    }, [stopProgressUpdates, onPlayStop]);

    /**
     * Seek to specific time
     */
    const seekTo = useCallback((timeInSeconds: number) => {
        if (!audioRef.current || !duration) return;

        const clampedTime = Math.max(0, Math.min(timeInSeconds, duration));
        audioRef.current.currentTime = clampedTime;
        setCurrentTime(clampedTime);
    }, [duration]);

    /**
     * Set volume
     */
    const setVolume = useCallback((newVolume: number) => {
        const clampedVolume = Math.max(0, Math.min(1, newVolume));
        setVolumeState(clampedVolume);

        if (audioRef.current) {
            audioRef.current.volume = isMuted ? 0 : clampedVolume;
        }

        onVolumeChange?.(clampedVolume, isMuted);
    }, [isMuted, onVolumeChange]);

    /**
     * Toggle mute
     */
    const toggleMute = useCallback(() => {
        const newMuted = !isMuted;
        setIsMuted(newMuted);

        if (audioRef.current) {
            audioRef.current.volume = newMuted ? 0 : volume;
        }

        onVolumeChange?.(volume, newMuted);
    }, [isMuted, volume, onVolumeChange]);

    /**
     * Set playback speed
     */
    const setSpeed = useCallback((newSpeed: PlaybackSpeed) => {
        setSpeedState(newSpeed);

        if (audioRef.current) {
            audioRef.current.playbackRate = newSpeed;
        }

        onSpeedChange?.(newSpeed);
    }, [onSpeedChange]);

    /**
     * Handle progress bar click for seeking
     */
    const handleProgressClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
        if (!duration || !showProgress) return;

        const rect = event.currentTarget.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const percentage = clickX / rect.width;
        const newTime = percentage * duration;

        seekTo(newTime);
    }, [duration, showProgress, seekTo]);

    /**
     * Skip backward (10 seconds)
     */
    const skipBackward = useCallback(() => {
        seekTo(Math.max(0, currentTime - 10));
    }, [currentTime, seekTo]);

    /**
     * Skip forward (10 seconds)
     */
    const skipForward = useCallback(() => {
        seekTo(Math.min(duration, currentTime + 10));
    }, [duration, currentTime, seekTo]);

    /**
     * Format time in MM:SS format
     */
    const formatTime = useCallback((timeInSeconds: number): string => {
        if (!timeInSeconds || isNaN(timeInSeconds)) return '00:00';

        const minutes = Math.floor(timeInSeconds / 60);
        const seconds = Math.floor(timeInSeconds % 60);
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, []);

    /**
     * Get volume icon based on current volume
     */
    const getVolumeIcon = useCallback(() => {
        if (isMuted || volume === 0) return VolumeX;
        if (volume < 0.5) return Volume1;
        return Volume2;
    }, [isMuted, volume]);

    /**
     * Get volume level for accessibility
     */
    const getVolumeLevel = useCallback((): VolumeLevel => {
        if (isMuted || volume === 0) return 'muted';
        if (volume < 0.33) return 'low';
        if (volume < 0.66) return 'medium';
        return 'high';
    }, [isMuted, volume]);

    // Expose ref methods for external control
    useImperativeHandle(ref, () => ({
        play,
        pause,
        stop,
        seekTo,
        setVolume,
        setSpeed,
        getCurrentTime: () => currentTime,
        getDuration: () => duration,
        getState: () => playbackState,
    }), [play, pause, stop, seekTo, setVolume, setSpeed, currentTime, duration, playbackState]);

    // Initialize audio when source changes
    useEffect(() => {
        if (src) {
            initializeAudio(src);
        } else {
            cleanup();
        }

        return cleanup;
    }, [src, initializeAudio, cleanup]);

    // Handle interruptions
    useEffect(() => {
        if (allowInterruption && playbackState === 'playing') {
            // This would be called by parent components to interrupt playback
            // The actual interruption logic is handled by the parent
        }
    }, [allowInterruption, playbackState]);

    // Cleanup on unmount
    useEffect(() => {
        return cleanup;
    }, [cleanup]);

    // Get accessibility labels
    const getAriaLabel = () => {
        switch (playbackState) {
            case 'playing':
                return `Playing audio, ${formatTime(currentTime)} of ${formatTime(duration)}`;
            case 'paused':
                return `Audio paused at ${formatTime(currentTime)} of ${formatTime(duration)}`;
            case 'loading':
                return 'Loading audio...';
            case 'error':
                return `Audio error: ${error}`;
            default:
                return 'Audio ready to play';
        }
    };

    if (!src) {
        return (
            <div className={`voice-player-empty text-center p-4 text-gray-500 ${className}`}>
                <AlertCircle className="w-8 h-8 mx-auto mb-2" />
                <p>No audio to play</p>
            </div>
        );
    }

    return (
        <div
            className={`voice-player bg-white dark:bg-gray-800 rounded-lg p-4 ${className}`}
            role="region"
            aria-label="Audio player"
        >
            {/* Error Display */}
            {error && (
                <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    {error}
                </div>
            )}

            {/* Main Controls */}
            {showControls && (
                <div className="flex items-center justify-center space-x-3 mb-4">

                    {/* Skip Backward */}
                    <button
                        onClick={skipBackward}
                        disabled={disabled || playbackState === 'loading' || !duration}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                        aria-label="Skip backward 10 seconds"
                    >
                        <SkipBack className="w-4 h-4" />
                    </button>

                    {/* Main Play/Pause Button */}
                    <button
                        onClick={playbackState === 'playing' ? pause : play}
                        disabled={disabled || playbackState === 'loading' || playbackState === 'error'}
                        className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-500 hover:bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label={getAriaLabel()}
                    >
                        {playbackState === 'loading' ? (
                            <Loader2 className="w-6 h-6 animate-spin" />
                        ) : playbackState === 'playing' ? (
                            <Pause className="w-6 h-6" />
                        ) : (
                            <Play className="w-6 h-6" />
                        )}
                    </button>

                    {/* Stop Button */}
                    <button
                        onClick={stop}
                        disabled={disabled || playbackState === 'idle' || playbackState === 'loading'}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                        aria-label="Stop playback"
                    >
                        <Square className="w-4 h-4" />
                    </button>

                    {/* Skip Forward */}
                    <button
                        onClick={skipForward}
                        disabled={disabled || playbackState === 'loading' || !duration}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                        aria-label="Skip forward 10 seconds"
                    >
                        <SkipForward className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Progress Bar */}
            {showProgress && (
                <div className="mb-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                        <span>{formatTime(currentTime)}</span>
                        <span>/</span>
                        <span>{formatTime(duration)}</span>
                    </div>

                    <div
                        className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full cursor-pointer"
                        onClick={handleProgressClick}
                        role="progressbar"
                        aria-valuenow={currentTime}
                        aria-valuemin={0}
                        aria-valuemax={duration}
                        aria-label={`Audio progress: ${formatTime(currentTime)} of ${formatTime(duration)}`}
                    >
                        <div
                            className="h-full bg-blue-500 rounded-full transition-all duration-100"
                            style={{ width: duration ? `${(currentTime / duration) * 100}%` : '0%' }}
                        />
                    </div>
                </div>
            )}

            {/* Volume and Speed Controls */}
            <div className="flex items-center justify-between">

                {/* Volume Control */}
                {enableVolumeControl && (
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={toggleMute}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                            aria-label={`Volume ${getVolumeLevel()}`}
                        >
                            {React.createElement(getVolumeIcon(), { className: "w-4 h-4" })}
                        </button>

                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={volume}
                            onChange={(e) => setVolume(parseFloat(e.target.value))}
                            className="w-20 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600"
                            aria-label="Volume control"
                        />
                    </div>
                )}

                {/* Speed Control */}
                {enableSpeedControl && (
                    <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Speed:</span>
                        <select
                            value={speed}
                            onChange={(e) => setSpeed(parseFloat(e.target.value) as PlaybackSpeed)}
                            className="text-sm border rounded px-2 py-1 bg-white dark:bg-gray-700 dark:border-gray-600"
                            aria-label="Playback speed"
                        >
                            <option value={0.5}>0.5x</option>
                            <option value={0.75}>0.75x</option>
                            <option value={1.0}>1x</option>
                            <option value={1.25}>1.25x</option>
                            <option value={1.5}>1.5x</option>
                            <option value={2.0}>2x</option>
                        </select>
                    </div>
                )}
            </div>
        </div>
    );
});

VoicePlayer.displayName = 'VoicePlayer';

export default VoicePlayer;