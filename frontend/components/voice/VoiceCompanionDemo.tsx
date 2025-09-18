/**
 * VoiceCompanionDemo - Integration Demo for VoiceCompanion Component
 * 
 * This demo showcases the complete voice interaction workflow:
 * - File-based recording with push-to-talk
 * - Backend integration with emotion analysis
 * - Cultural context and crisis detection
 * - TTS playback with accessible controls
 * - ChatPane-compatible UI integration
 */

'use client';

import React, { useState, useCallback } from 'react';
import { VoiceCompanion } from './VoiceCompanion';
import { VoiceEmotionAnalysis, VoiceLanguageCode } from './types';
import { Settings, Info, AlertTriangle, Heart, Globe } from 'lucide-react';

/**
 * Demo interface for VoiceCompanion integration
 */
export const VoiceCompanionDemo: React.FC = () => {
    // Demo state
    const [authToken] = useState<string>('demo-token-123'); // In real app, get from useUser hook
    const [language, setLanguage] = useState<VoiceLanguageCode>('en-US');
    const [familyContext, setFamilyContext] = useState<'individual' | 'family-aware' | 'elder-present'>('individual');
    const [greetingStyle, setGreetingStyle] = useState<'formal' | 'informal' | 'traditional'>('informal');
    const [chatPaneMode, setChatPaneMode] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(true);
    const [crisisThreshold, setCrisisThreshold] = useState(0.7);

    // Interaction logs
    const [interactionLog, setInteractionLog] = useState<Array<{
        timestamp: Date;
        transcription: string;
        response: string;
        emotion: VoiceEmotionAnalysis;
        crisisScore?: number;
    }>>([]);

    const [crisisAlerts, setCrisisAlerts] = useState<Array<{
        timestamp: Date;
        score: number;
        actions: string[];
    }>>([]);

    /**
     * Handle completed voice interactions
     */
    const handleInteractionComplete = useCallback((
        transcription: string,
        response: string,
        emotion: VoiceEmotionAnalysis
    ) => {
        console.log('Voice interaction completed:', { transcription, response, emotion });

        setInteractionLog(prev => [...prev, {
            timestamp: new Date(),
            transcription,
            response,
            emotion
        }].slice(-10)); // Keep last 10 interactions
    }, []);

    /**
     * Handle crisis detection
     */
    const handleCrisisDetected = useCallback((crisisScore: number, suggestedActions: string[]) => {
        console.log('Crisis detected:', { crisisScore, suggestedActions });

        setCrisisAlerts(prev => [...prev, {
            timestamp: new Date(),
            score: crisisScore,
            actions: suggestedActions
        }].slice(-5)); // Keep last 5 alerts

        // In real app, would trigger crisis intervention workflow
        alert(`Crisis Level Detected (${Math.round(crisisScore * 100)}%)\n\nSuggested Actions:\n${suggestedActions.join('\n')}\n\nTele MANAS: 14416`);
    }, []);

    /**
     * Cultural context configuration
     */
    const culturalContext = {
        language,
        familyContext,
        greetingStyle,
    };

    /**
     * Demo controls for testing different configurations
     */
    const DemoControls = () => (
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border mb-6">
            <div className="flex items-center mb-3">
                <Settings className="w-4 h-4 text-gray-600 mr-2" />
                <h3 className="font-medium text-gray-800 dark:text-gray-200">Demo Configuration</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                {/* Language Selection */}
                <div>
                    <label className="block text-gray-600 dark:text-gray-400 mb-1">Language</label>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value as VoiceLanguageCode)}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                        <option value="en-US">English (US)</option>
                        <option value="hi-IN">Hindi (India)</option>
                        <option value="ta-IN">Tamil (India)</option>
                        <option value="te-IN">Telugu (India)</option>
                    </select>
                </div>

                {/* Family Context */}
                <div>
                    <label className="block text-gray-600 dark:text-gray-400 mb-1">Family Context</label>
                    <select
                        value={familyContext}
                        onChange={(e) => setFamilyContext(e.target.value as any)}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                        <option value="individual">Individual</option>
                        <option value="family-aware">Family Aware</option>
                        <option value="elder-present">Elder Present</option>
                    </select>
                </div>

                {/* Greeting Style */}
                <div>
                    <label className="block text-gray-600 dark:text-gray-400 mb-1">Greeting Style</label>
                    <select
                        value={greetingStyle}
                        onChange={(e) => setGreetingStyle(e.target.value as any)}
                        className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                    >
                        <option value="informal">Informal</option>
                        <option value="formal">Formal</option>
                        <option value="traditional">Traditional</option>
                    </select>
                </div>

                {/* Crisis Threshold */}
                <div>
                    <label className="block text-gray-600 dark:text-gray-400 mb-1">
                        Crisis Threshold ({Math.round(crisisThreshold * 100)}%)
                    </label>
                    <input
                        type="range"
                        min="0.3"
                        max="0.9"
                        step="0.1"
                        value={crisisThreshold}
                        onChange={(e) => setCrisisThreshold(parseFloat(e.target.value))}
                        className="w-full"
                    />
                </div>

                {/* UI Mode */}
                <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={chatPaneMode}
                            onChange={(e) => setChatPaneMode(e.target.checked)}
                            className="mr-2"
                        />
                        Chat Pane Mode
                    </label>
                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={showAdvanced}
                            onChange={(e) => setShowAdvanced(e.target.checked)}
                            className="mr-2"
                        />
                        Show Advanced
                    </label>
                </div>
            </div>
        </div>
    );

    /**
     * Interaction history display
     */
    const InteractionHistory = () => (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Recent Interactions */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
                <div className="flex items-center mb-3">
                    <Info className="w-4 h-4 text-blue-600 mr-2" />
                    <h3 className="font-medium text-gray-800 dark:text-gray-200">Recent Interactions</h3>
                    <span className="ml-auto text-xs text-gray-500">Last {interactionLog.length}</span>
                </div>

                <div className="space-y-3 max-h-64 overflow-y-auto">
                    {interactionLog.length === 0 ? (
                        <p className="text-gray-500 text-sm text-center py-4">
                            No interactions yet. Try speaking to MITRA!
                        </p>
                    ) : (
                        interactionLog.slice().reverse().map((interaction, index) => (
                            <div key={index} className="border-l-2 border-blue-200 pl-3 text-sm">
                                <div className="text-xs text-gray-500 mb-1">
                                    {interaction.timestamp.toLocaleTimeString()}
                                </div>
                                <div className="text-blue-700 dark:text-blue-300 mb-1">
                                    <strong>You:</strong> {interaction.transcription}
                                </div>
                                <div className="text-green-700 dark:text-green-300 mb-1">
                                    <strong>MITRA:</strong> {interaction.response}
                                </div>
                                <div className="text-pink-600 dark:text-pink-400 text-xs">
                                    <Heart className="w-3 h-3 inline mr-1" />
                                    {interaction.emotion.primaryEmotion} ({Math.round(interaction.emotion.confidence * 100)}%)
                                    • Stress: {Math.round(interaction.emotion.stressLevel * 100)}%
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Crisis Alerts */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
                <div className="flex items-center mb-3">
                    <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
                    <h3 className="font-medium text-gray-800 dark:text-gray-200">Crisis Alerts</h3>
                    <span className="ml-auto text-xs text-gray-500">Last {crisisAlerts.length}</span>
                </div>

                <div className="space-y-3 max-h-64 overflow-y-auto">
                    {crisisAlerts.length === 0 ? (
                        <p className="text-gray-500 text-sm text-center py-4">
                            No crisis alerts. Mental health monitoring active.
                        </p>
                    ) : (
                        crisisAlerts.slice().reverse().map((alert, index) => (
                            <div key={index} className="border-l-2 border-red-200 pl-3 text-sm">
                                <div className="text-xs text-gray-500 mb-1">
                                    {alert.timestamp.toLocaleTimeString()}
                                </div>
                                <div className="text-red-700 dark:text-red-300 font-medium mb-1">
                                    Crisis Score: {Math.round(alert.score * 100)}%
                                </div>
                                <div className="text-gray-600 dark:text-gray-400 text-xs">
                                    <strong>Actions:</strong> {alert.actions.join(', ')}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto p-6">
            {/* Demo Header */}
            <div className="text-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-2">
                    MITRA Voice Companion Demo
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Complete file-based voice interaction with cultural context, emotion analysis, and crisis detection
                </p>
                <div className="flex items-center justify-center mt-2 text-sm text-blue-600">
                    <Globe className="w-4 h-4 mr-1" />
                    Supports Hindi, English, Tamil, Telugu • Cultural Mental Health AI
                </div>
            </div>

            {/* Demo Controls */}
            <DemoControls />

            {/* Main VoiceCompanion Component */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border shadow-sm">
                <VoiceCompanion
                    authToken={authToken}
                    culturalContext={culturalContext}
                    crisisThreshold={crisisThreshold}
                    onCrisisDetected={handleCrisisDetected}
                    onInteractionComplete={handleInteractionComplete}
                    chatPaneMode={chatPaneMode}
                    showAdvancedControls={showAdvanced}
                    className="voice-companion-demo"
                />
            </div>

            {/* Interaction History */}
            <InteractionHistory />

            {/* Integration Notes */}
            <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center mb-2">
                    <Info className="w-4 h-4 text-blue-600 mr-2" />
                    <h3 className="font-medium text-blue-800 dark:text-blue-200">Integration Notes</h3>
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                    <p>• This demo showcases the complete VoiceCompanion integration with all features</p>
                    <p>• In your app, import from: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">components/voice/VoiceCompanion</code></p>
                    <p>• Use <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">chatPaneMode=true</code> for ChatPane integration</p>
                    <p>• Requires backend endpoints: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">/api/v1/voice/pipeline/audio</code></p>
                    <p>• Crisis detection automatically escalates to Tele MANAS (14416) support</p>
                </div>
            </div>
        </div>
    );
};

export default VoiceCompanionDemo;