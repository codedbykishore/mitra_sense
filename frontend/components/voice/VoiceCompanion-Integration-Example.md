# VoiceCompanion Integration Example for MITRA Sense

This example shows how to integrate the VoiceCompanion with the existing ChatPane.jsx component in MITRA Sense.

## 1. Enhanced ChatPane with Voice Support

```jsx
// components/EnhancedChatPane.jsx
import React, { useState, useCallback } from 'react';
import { VoiceCompanion } from './voice/VoiceCompanion';
import { ChatPane } from './ChatPane';
import { useUser } from '../hooks/useUser';
import { Mic, MicOff, MessageCircle, Volume2 } from 'lucide-react';

export const EnhancedChatPane = () => {
  const { user, authToken } = useUser();
  const [voiceMode, setVoiceMode] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  
  // Cultural context based on user preferences
  const culturalContext = {
    language: user?.preferredLanguage || 'en-US',
    familyContext: user?.familyContext || 'individual',
    greetingStyle: user?.greetingStyle || 'informal',
  };

  const handleVoiceInteraction = useCallback((transcription, response, emotion) => {
    // Add voice interaction to chat history
    const voiceEntry = {
      id: Date.now(),
      type: 'voice',
      userMessage: transcription,
      assistantMessage: response,
      emotion: emotion.primaryEmotion,
      stressLevel: emotion.stressLevel,
      timestamp: new Date(),
    };
    
    setChatHistory(prev => [...prev, voiceEntry]);
  }, []);

  const handleCrisisDetection = useCallback((crisisScore, suggestedActions) => {
    // Emergency response protocol
    console.log('🚨 Crisis detected:', { crisisScore, suggestedActions });
    
    // Add crisis alert to chat
    const crisisEntry = {
      id: Date.now(),
      type: 'crisis',
      message: `Crisis level detected (${Math.round(crisisScore * 100)}%). Immediate support available.`,
      actions: suggestedActions,
      timestamp: new Date(),
    };
    
    setChatHistory(prev => [...prev, crisisEntry]);
    
    // Show emergency contact modal
    showEmergencySupport();
  }, []);

  return (
    <div className="chat-interface h-full flex flex-col">
      {/* Chat Header with Voice Toggle */}
      <div className="chat-header p-4 border-b bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            MITRA Mental Health Support
          </h2>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setVoiceMode(!voiceMode)}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                voiceMode 
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
              }`}
              aria-label={voiceMode ? 'Switch to text chat' : 'Switch to voice chat'}
            >
              {voiceMode ? (
                <>
                  <Volume2 className="w-4 h-4 mr-2" />
                  Voice Mode
                </>
              ) : (
                <>
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Text Mode
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-hidden">
        {voiceMode ? (
          // Voice Companion Interface
          <VoiceCompanion
            authToken={authToken}
            culturalContext={culturalContext}
            crisisThreshold={0.7}
            onCrisisDetected={handleCrisisDetection}
            onInteractionComplete={handleVoiceInteraction}
            chatPaneMode={true}
            showAdvancedControls={true}
            className="h-full"
          />
        ) : (
          // Traditional Text Chat
          <ChatPane 
            chatHistory={chatHistory}
            onNewMessage={(message) => {
              // Handle text messages
              setChatHistory(prev => [...prev, {
                id: Date.now(),
                type: 'text',
                userMessage: message,
                timestamp: new Date(),
              }]);
            }}
          />
        )}
      </div>

      {/* Chat History Integration */}
      {chatHistory.length > 0 && (
        <div className="chat-history-summary p-3 bg-gray-50 dark:bg-gray-800 border-t">
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Session: {chatHistory.length} interactions
            {chatHistory.some(entry => entry.type === 'crisis') && (
              <span className="ml-2 text-red-600">⚠️ Crisis detected</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Emergency support modal
const showEmergencySupport = () => {
  // Implementation for emergency contact modal
  alert(`🚨 IMMEDIATE SUPPORT AVAILABLE 🚨\n\nTele MANAS: 14416 (24/7 Crisis Support)\n\nYou are not alone. Help is available immediately.`);
};
```

## 2. App Integration

```jsx
// app/page.tsx (or main app component)
import { EnhancedChatPane } from '@/components/EnhancedChatPane';
import { useUser } from '@/hooks/useUser';

export default function Home() {
  const { user } = useUser();

  if (!user) {
    return <Login />;
  }

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="container mx-auto max-w-4xl">
        <EnhancedChatPane />
      </div>
    </main>
  );
}
```

## 3. User Settings Integration

```jsx
// components/UserSettings.jsx
import { useState } from 'react';
import { useUser } from '../hooks/useUser';

export const UserSettings = () => {
  const { user, updateUserSettings } = useUser();
  
  const handleVoiceSettingsUpdate = (settings) => {
    updateUserSettings({
      ...user,
      preferredLanguage: settings.language,
      familyContext: settings.familyContext,
      greetingStyle: settings.greetingStyle,
      crisisThreshold: settings.crisisThreshold,
    });
  };

  return (
    <div className="settings-panel">
      <h3>Voice Companion Settings</h3>
      
      <div className="setting-group">
        <label>Preferred Language</label>
        <select 
          value={user?.preferredLanguage || 'en-US'}
          onChange={(e) => handleVoiceSettingsUpdate({
            ...user,
            language: e.target.value
          })}
        >
          <option value="en-US">English (US)</option>
          <option value="hi-IN">Hindi (India)</option>
          <option value="ta-IN">Tamil (India)</option>
          <option value="te-IN">Telugu (India)</option>
        </select>
      </div>

      <div className="setting-group">
        <label>Family Context</label>
        <select 
          value={user?.familyContext || 'individual'}
          onChange={(e) => handleVoiceSettingsUpdate({
            ...user,
            familyContext: e.target.value
          })}
        >
          <option value="individual">Individual Support</option>
          <option value="family-aware">Family-Aware Support</option>
          <option value="elder-present">Elder-Present Context</option>
        </select>
      </div>

      <div className="setting-group">
        <label>Greeting Style</label>
        <select 
          value={user?.greetingStyle || 'informal'}
          onChange={(e) => handleVoiceSettingsUpdate({
            ...user,
            greetingStyle: e.target.value
          })}
        >
          <option value="informal">Informal</option>
          <option value="formal">Formal</option>
          <option value="traditional">Traditional</option>
        </select>
      </div>
    </div>
  );
};
```

## 4. Crisis Management Integration

```jsx
// services/crisisService.js
export class CrisisService {
  static handleCrisisDetection(crisisScore, suggestedActions, userContext) {
    // Log crisis incident
    this.logCrisisIncident({
      userId: userContext.userId,
      crisisScore,
      suggestedActions,
      timestamp: new Date(),
      culturalContext: userContext.culturalContext,
    });

    // Immediate interventions based on severity
    if (crisisScore >= 0.9) {
      this.triggerImmediateIntervention(userContext);
    } else if (crisisScore >= 0.7) {
      this.triggerSupportAlert(userContext);
    }

    // Family notification (if family-aware context)
    if (userContext.familyContext === 'family-aware' && crisisScore >= 0.8) {
      this.notifyEmergencyContact(userContext);
    }

    return {
      interventionLevel: this.getInterventionLevel(crisisScore),
      supportResources: this.getSupportResources(userContext.culturalContext),
      followUpRequired: crisisScore >= 0.6,
    };
  }

  static getSupportResources(culturalContext) {
    const resources = {
      'hi-IN': {
        emergency: 'Tele MANAS: 14416',
        message: 'आपको तुरंत सहायता चाहिए। कृपया 14416 पर कॉल करें।',
        local: ['NIMHANS', 'Vandrevala Foundation']
      },
      'en-US': {
        emergency: 'Tele MANAS: 14416',
        message: 'Immediate support is available. Please call 14416.',
        local: ['NIMHANS', 'Vandrevala Foundation']
      }
    };

    return resources[culturalContext.language] || resources['en-US'];
  }
}
```

## 5. Analytics Integration

```jsx
// services/voiceAnalytics.js
export class VoiceAnalytics {
  static trackVoiceInteraction(interaction) {
    // Track voice usage patterns
    this.analytics.track('voice_interaction', {
      duration: interaction.duration,
      language: interaction.culturalContext.language,
      emotionDetected: interaction.emotion.primaryEmotion,
      stressLevel: interaction.emotion.stressLevel,
      crisisScore: interaction.crisisScore,
      successful: interaction.completed,
    });

    // Mental health progression tracking
    this.trackMentalHealthProgression({
      userId: interaction.userId,
      sessionId: interaction.sessionId,
      emotionalState: interaction.emotion,
      interventionRequired: interaction.crisisScore >= 0.7,
    });
  }

  static generateWellnessReport(userId, timeframe = '7d') {
    // Generate insights from voice interactions
    return {
      emotionalTrends: this.getEmotionalTrends(userId, timeframe),
      stressPatterns: this.getStressPatterns(userId, timeframe),
      interventions: this.getInterventions(userId, timeframe),
      recommendations: this.getRecommendations(userId),
    };
  }
}
```

## 6. Backend Integration Points

```python
# app/routes/voice.py - Enhanced voice endpoints for VoiceCompanion

@router.post("/pipeline/audio", response_model=VoiceInteractionResponse)
async def process_voice_interaction(
    audio_file: UploadFile = File(...),
    cultural_context: str = Form(...),
    conversation_id: str = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    """Complete voice processing pipeline for VoiceCompanion"""
    
    # Parse cultural context
    context = json.loads(cultural_context)
    
    # Process audio through complete pipeline
    try:
        # 1. Speech-to-Text with language detection
        transcription = await speech_service.transcribe_audio(
            audio_file, 
            language_hint=context['language']
        )
        
        # 2. Emotion analysis from voice characteristics
        emotion_analysis = await speech_service.analyze_emotion(
            audio_file,
            transcription.text
        )
        
        # 3. AI response with cultural context and crisis detection
        ai_response = await gemini_service.process_cultural_conversation(
            transcription.text,
            language=context['language'],
            cultural_context=context,
            conversation_id=conversation_id,
            emotion_context=emotion_analysis
        )
        
        # 4. Text-to-Speech with cultural voice selection
        tts_audio = await speech_service.synthesize_speech(
            ai_response.text,
            language=context['language'],
            voice_style=context.get('greetingStyle', 'informal')
        )
        
        # 5. Crisis detection and logging
        if ai_response.crisis_score >= 0.7:
            await crisis_service.handle_crisis_detection(
                user_id=user_id,
                crisis_score=ai_response.crisis_score,
                context=context,
                transcription=transcription.text
            )
        
        # 6. Analytics and session tracking
        await analytics_service.track_voice_interaction(
            user_id=user_id,
            conversation_id=conversation_id,
            interaction_data={
                'transcription': transcription,
                'emotion': emotion_analysis,
                'ai_response': ai_response,
                'cultural_context': context
            }
        )
        
        return VoiceInteractionResponse(
            transcription=transcription,
            ai_response=ai_response,
            emotion=emotion_analysis,
            tts_audio=tts_audio,
            conversation_id=conversation_id or str(uuid.uuid4()),
            session_metadata=await get_session_metadata(user_id)
        )
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        
        # Fallback response for technical errors
        fallback_response = await get_fallback_response(
            context['language'], 
            str(e)
        )
        
        return VoiceInteractionResponse(
            transcription={"text": "Audio processing failed", "confidence": 0.0},
            ai_response=fallback_response,
            emotion=default_emotion_state,
            tts_audio=None,
            error="technical_error"
        )
```

This integration example demonstrates how VoiceCompanion seamlessly integrates with the existing MITRA Sense architecture while providing comprehensive voice interaction capabilities with cultural sensitivity and crisis detection.