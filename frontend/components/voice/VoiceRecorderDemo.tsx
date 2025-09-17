'use client';

import React, { useState } from 'react';
import VoiceRecorder from './VoiceRecorder';
import { VoiceRecordingError, AudioBlobWithMetadata } from './types';
import { Download, Play, AlertCircle, CheckCircle } from 'lucide-react';

/**
 * Demo component showing how to use the VoiceRecorder
 * This demonstrates the complete file-based voice recording workflow
 */
export const VoiceRecorderDemo: React.FC = () => {
    const [recordedAudio, setRecordedAudio] = useState<AudioBlobWithMetadata | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');

    /**
     * Handle successful recording completion
     */
    const handleRecordingComplete = (audioBlob: Blob, duration: number) => {
        console.log('Recording completed:', { size: audioBlob.size, duration });

        const audioData: AudioBlobWithMetadata = {
            blob: audioBlob,
            duration,
            format: audioBlob.type,
            size: audioBlob.size,
            timestamp: new Date(),
            quality: {
                // These would be populated from actual recording metadata
                bitrate: 128000,
                sampleRate: 44100,
                channels: 1,
            }
        };

        setRecordedAudio(audioData);
        setError('');
        setSuccess(`Recording saved successfully! Duration: ${formatDuration(duration)}`);

        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
    };

    /**
     * Handle recording errors
     */
    const handleRecordingError = (errorType: VoiceRecordingError, message: string) => {
        console.error('Recording error:', errorType, message);
        setError(message);
        setSuccess('');

        // Clear error after 5 seconds
        setTimeout(() => setError(''), 5000);
    };

    /**
     * Play the recorded audio
     */
    const playRecording = () => {
        if (!recordedAudio) return;

        const audioUrl = URL.createObjectURL(recordedAudio.blob);
        const audio = new Audio(audioUrl);

        setIsPlaying(true);

        audio.onended = () => {
            setIsPlaying(false);
            URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = () => {
            setIsPlaying(false);
            setError('Failed to play audio');
            URL.revokeObjectURL(audioUrl);
        };

        audio.play().catch(err => {
            console.error('Playback error:', err);
            setIsPlaying(false);
            setError('Failed to play audio');
            URL.revokeObjectURL(audioUrl);
        });
    };

    /**
     * Download the recorded audio
     */
    const downloadRecording = () => {
        if (!recordedAudio) return;

        const url = URL.createObjectURL(recordedAudio.blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voice-recording-${new Date().toISOString()}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    /**
     * Clear the current recording
     */
    const clearRecording = () => {
        setRecordedAudio(null);
        setError('');
        setSuccess('');
    };

    /**
     * Format duration in MM:SS format
     */
    const formatDuration = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    /**
     * Format file size in human readable format
     */
    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-white">
                Voice Recorder Demo
            </h2>

            {/* Success Message */}
            {success && (
                <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-md flex items-center">
                    <CheckCircle size={16} className="mr-2" />
                    {success}
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md flex items-center">
                    <AlertCircle size={16} className="mr-2" />
                    {error}
                </div>
            )}

            {/* Voice Recorder Component */}
            <div className="mb-6">
                <VoiceRecorder
                    onRecordingComplete={handleRecordingComplete}
                    onError={handleRecordingError}
                    maxDuration={180} // 3 minutes
                    className="w-full"
                />
            </div>

            {/* Recorded Audio Info */}
            {recordedAudio && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
                    <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">
                        Recorded Audio
                    </h3>

                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                        <div>Duration: {formatDuration(recordedAudio.duration)}</div>
                        <div>Size: {formatFileSize(recordedAudio.size)}</div>
                        <div>Format: {recordedAudio.format}</div>
                        <div>Recorded: {recordedAudio.timestamp.toLocaleTimeString()}</div>
                    </div>

                    {/* Audio Controls */}
                    <div className="flex space-x-2 mt-4">
                        <button
                            onClick={playRecording}
                            disabled={isPlaying}
                            className="flex items-center px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
                        >
                            <Play size={16} className="mr-1" />
                            {isPlaying ? 'Playing...' : 'Play'}
                        </button>

                        <button
                            onClick={downloadRecording}
                            className="flex items-center px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
                        >
                            <Download size={16} className="mr-1" />
                            Download
                        </button>

                        <button
                            onClick={clearRecording}
                            className="px-3 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            )}

            {/* Instructions */}
            <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                <p className="mb-1">
                    Click the microphone button to start recording.
                </p>
                <p className="mb-1">
                    Click the stop button or wait for automatic stop after 3 minutes.
                </p>
                <p>
                    The recorded audio will be captured as a Blob for upload to your backend.
                </p>
            </div>

            {/* Technical Info */}
            <details className="mt-4">
                <summary className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                    Technical Details
                </summary>
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 space-y-1">
                    <p>• Uses MediaRecorder API with WebM/Opus codec</p>
                    <p>• Automatic fallback to supported formats</p>
                    <p>• Built-in noise suppression and echo cancellation</p>
                    <p>• 128kbps bitrate for good quality</p>
                    <p>• Microphone permission handling</p>
                    <p>• Browser compatibility checks</p>
                </div>
            </details>
        </div>
    );
};

export default VoiceRecorderDemo;