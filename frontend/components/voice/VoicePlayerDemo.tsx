'use client';

import React, { useState, useRef } from 'react';
import VoicePlayer, { VoicePlayerRef, PlaybackSpeed } from './VoicePlayer';
import { VoiceRecorder } from './VoiceRecorder';
import { VoicePlaybackError } from './types';
import { Upload, Download, Trash2, Music } from 'lucide-react';

/**
 * Demo component showing VoicePlayer usage and integration
 * Demonstrates all features including external control and interruption handling
 */
export const VoicePlayerDemo: React.FC = () => {
    const [audioSrc, setAudioSrc] = useState<string | Blob | null>(null);
    const [audioName, setAudioName] = useState<string>('');
    const [isRecording, setIsRecording] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);

    // Refs for external control
    const playerRef = useRef<VoicePlayerRef>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    /**
     * Add log entry with timestamp
     */
    const addLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 9)]);
    };

    /**
     * Handle file upload
     */
    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            if (file.type.startsWith('audio/')) {
                setAudioSrc(file);
                setAudioName(file.name);
                addLog(`Loaded audio file: ${file.name}`);
            } else {
                addLog('Error: Please select an audio file');
            }
        }
    };

    /**
     * Handle recording completion from VoiceRecorder
     */
    const handleRecordingComplete = (audioBlob: Blob, duration: number) => {
        setAudioSrc(audioBlob);
        setAudioName(`Recording ${new Date().toLocaleTimeString()}`);
        setIsRecording(false);
        addLog(`New recording completed: ${duration.toFixed(1)}s`);
    };

    /**
     * Handle recording error
     */
    const handleRecordingError = (error: any, message: string) => {
        setIsRecording(false);
        addLog(`Recording error: ${message}`);
    };

    /**
     * Clear current audio
     */
    const clearAudio = () => {
        setAudioSrc(null);
        setAudioName('');
        addLog('Audio cleared');
    };

    /**
     * Download current audio (if it's a blob)
     */
    const downloadAudio = () => {
        if (audioSrc instanceof Blob) {
            const url = URL.createObjectURL(audioSrc);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${audioName || 'audio'}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            addLog(`Downloaded: ${audioName}`);
        }
    };

    /**
     * External control functions
     */
    const externalPlay = () => {
        playerRef.current?.play();
        addLog('External play command');
    };

    const externalPause = () => {
        playerRef.current?.pause();
        addLog('External pause command');
    };

    const externalStop = () => {
        playerRef.current?.stop();
        addLog('External stop command');
    };

    const externalSeek = (time: number) => {
        playerRef.current?.seekTo(time);
        addLog(`External seek to ${time}s`);
    };

    const externalVolumeChange = (volume: number) => {
        playerRef.current?.setVolume(volume);
        addLog(`External volume set to ${Math.round(volume * 100)}%`);
    };

    const externalSpeedChange = (speed: PlaybackSpeed) => {
        playerRef.current?.setSpeed(speed);
        addLog(`External speed set to ${speed}x`);
    };

    /**
     * Interrupt playback (simulates recording interruption)
     */
    const simulateInterruption = () => {
        if (playerRef.current?.getState() === 'playing') {
            playerRef.current?.stop();
            addLog('Playback interrupted');
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">

            {/* Header */}
            <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
                    VoicePlayer Demo
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    Complete audio player with controls, progress, volume, and external control
                </p>
            </div>

            {/* Audio Source Management */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">Audio Source</h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

                    {/* File Upload */}
                    <div className="space-y-2">
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="w-full flex items-center justify-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                        >
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Audio File
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="audio/*"
                            onChange={handleFileUpload}
                            className="hidden"
                        />
                    </div>

                    {/* Voice Recording */}
                    <div className="flex justify-center">
                        <VoiceRecorder
                            onRecordingComplete={handleRecordingComplete}
                            onError={handleRecordingError}
                            disabled={isRecording}
                            maxDuration={60}
                        />
                    </div>

                    {/* Actions */}
                    <div className="space-y-2">
                        {audioSrc instanceof Blob && (
                            <button
                                onClick={downloadAudio}
                                className="w-full flex items-center justify-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Download
                            </button>
                        )}

                        {audioSrc && (
                            <button
                                onClick={clearAudio}
                                className="w-full flex items-center justify-center px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                            >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Clear Audio
                            </button>
                        )}
                    </div>
                </div>

                {/* Current Audio Info */}
                {audioSrc && (
                    <div className="mt-4 p-3 bg-white dark:bg-gray-700 rounded border">
                        <div className="flex items-center">
                            <Music className="w-4 h-4 mr-2 text-blue-500" />
                            <span className="font-medium">Current Audio:</span>
                            <span className="ml-2 text-gray-600 dark:text-gray-400">{audioName}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Voice Player */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold">Voice Player</h3>
                </div>

                <div className="p-6">
                    <VoicePlayer
                        ref={playerRef}
                        src={audioSrc}
                        autoPlay={false}
                        showControls={true}
                        enableVolumeControl={true}
                        enableSpeedControl={true}
                        showProgress={true}
                        allowInterruption={true}

                        // Event callbacks
                        onPlayStart={() => addLog('▶️ Playback started')}
                        onPlayPause={() => addLog('⏸️ Playback paused')}
                        onPlayStop={() => addLog('⏹️ Playback stopped')}
                        onPlayEnd={() => addLog('🏁 Playback ended')}
                        onError={(error: VoicePlaybackError, message: string) => addLog(`❌ Error: ${message}`)}
                        onProgress={(current, duration, percentage) => {
                            if (Math.floor(current) % 5 === 0 && current % 1 < 0.1) { // Log every 5 seconds
                                addLog(`📊 Progress: ${percentage.toFixed(1)}%`);
                            }
                        }}
                        onVolumeChange={(volume, isMuted) => addLog(`🔊 Volume: ${isMuted ? 'Muted' : Math.round(volume * 100) + '%'}`)}
                        onSpeedChange={(speed) => addLog(`⚡ Speed: ${speed}x`)}
                    />
                </div>
            </div>

            {/* External Controls */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">External Controls (Ref API)</h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <button
                        onClick={externalPlay}
                        className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                        Play
                    </button>

                    <button
                        onClick={externalPause}
                        className="px-3 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                    >
                        Pause
                    </button>

                    <button
                        onClick={externalStop}
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                        Stop
                    </button>

                    <button
                        onClick={simulateInterruption}
                        className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
                    >
                        Interrupt
                    </button>
                </div>

                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                    {/* Seek Controls */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Seek to:</label>
                        <div className="flex space-x-2">
                            <button onClick={() => externalSeek(0)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">0s</button>
                            <button onClick={() => externalSeek(10)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">10s</button>
                            <button onClick={() => externalSeek(30)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">30s</button>
                        </div>
                    </div>

                    {/* Volume Controls */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Set Volume:</label>
                        <div className="flex space-x-2">
                            <button onClick={() => externalVolumeChange(0)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">0%</button>
                            <button onClick={() => externalVolumeChange(0.5)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">50%</button>
                            <button onClick={() => externalVolumeChange(1)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">100%</button>
                        </div>
                    </div>

                    {/* Speed Controls */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Set Speed:</label>
                        <div className="flex space-x-2">
                            <button onClick={() => externalSpeedChange(0.5)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">0.5x</button>
                            <button onClick={() => externalSpeedChange(1)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">1x</button>
                            <button onClick={() => externalSpeedChange(2)} className="px-2 py-1 bg-gray-500 text-white rounded text-sm">2x</button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Event Log */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">Event Log</h3>

                <div className="bg-black text-green-400 rounded p-3 h-48 overflow-y-auto font-mono text-sm">
                    {logs.length === 0 ? (
                        <div className="text-gray-500">Events will appear here...</div>
                    ) : (
                        logs.map((log, index) => (
                            <div key={index} className="mb-1">{log}</div>
                        ))
                    )}
                </div>

                <button
                    onClick={() => setLogs([])}
                    className="mt-2 px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
                >
                    Clear Log
                </button>
            </div>

            {/* Feature Overview */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 text-blue-800 dark:text-blue-200">
                    Features Demonstrated
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">Player Features:</h4>
                        <ul className="space-y-1 text-blue-600 dark:text-blue-400">
                            <li>• Play, pause, stop controls</li>
                            <li>• Progress bar with seeking</li>
                            <li>• Volume control with mute</li>
                            <li>• Playback speed adjustment</li>
                            <li>• Skip forward/backward (10s)</li>
                            <li>• Time display (current/total)</li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">Integration Features:</h4>
                        <ul className="space-y-1 text-blue-600 dark:text-blue-400">
                            <li>• External control via ref API</li>
                            <li>• Event callbacks for all actions</li>
                            <li>• Interruption handling</li>
                            <li>• File upload and recording support</li>
                            <li>• Blob and URL source support</li>
                            <li>• Accessibility features</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VoicePlayerDemo;