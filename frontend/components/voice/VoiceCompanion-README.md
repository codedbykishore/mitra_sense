# VoiceCompanion Integration Guide

## Overview

The **VoiceCompanion** component provides a complete file-based voice interaction system for MITRA Sense, integrating recording, AI processing, and playback into a unified interface.

## Features

### 🎤 Voice Recording
- **File-based recording** with MediaRecorder API
- **Push-to-talk interface** with visual feedback
- **Duration limits** and automatic stopping
- **Permission handling** with user-friendly prompts
- **Error recovery** for recording failures

### 🤖 AI Integration
- **Complete backend pipeline** via `/api/v1/voice/pipeline/audio`
- **Speech-to-text** with language detection
- **Emotion analysis** with voice characteristics
- **RAG-enhanced responses** with cultural context
- **Text-to-speech** with natural voice synthesis

### 🛡️ Crisis Detection
- **Real-time monitoring** of emotional stress levels
- **Automatic escalation** when crisis threshold exceeded
- **Tele MANAS integration** for immediate support (14416)
- **Family-sensitive** crisis response protocols

### 🌏 Cultural Intelligence
- **Hindi/English code-switching** support
- **Cultural greeting styles** (formal, informal, traditional)
- **Family context awareness** (individual, family-aware, elder-present)
- **Regional language support** (Tamil, Telugu planned)

### ♿ Accessibility
- **Screen reader announcements** for all state changes
- **ARIA labels** and keyboard navigation
- **Visual progress indicators** for audio processing
- **Interruption handling** for voice conflicts

## Basic Usage

```tsx
import { VoiceCompanion } from '@/components/voice/VoiceCompanion';
import { useUser } from '@/hooks/useUser';

function ChatInterface() {
  const { user, authToken } = useUser();

  const handleCrisis = (score: number, actions: string[]) => {
    // Handle crisis detection
    console.log('Crisis detected:', score, actions);
    // Trigger emergency protocols
  };

  const handleInteraction = (transcription: string, response: string, emotion: any) => {
    // Log conversation for mental health tracking
    console.log('Voice interaction:', { transcription, response, emotion });
  };

  return (
    <VoiceCompanion
      authToken={authToken}
      culturalContext={{
        language: 'hi-IN',
        familyContext: 'family-aware',
        greetingStyle: 'traditional'
      }}
      crisisThreshold={0.7}
      onCrisisDetected={handleCrisis}
      onInteractionComplete={handleInteraction}
      chatPaneMode={true}
      showAdvancedControls={true}
    />
  );
}
```

## Integration with ChatPane

To integrate with existing ChatPane component:

```tsx
import { VoiceCompanion } from '@/components/voice';
import { ChatPane } from '@/components/ChatPane';

function EnhancedChatInterface() {
  return (
    <div className="chat-interface">
      {/* Existing text chat */}
      <ChatPane />
      
      {/* Voice companion overlay */}
      <div className="voice-overlay">
        <VoiceCompanion
          chatPaneMode={true}
          culturalContext={{
            language: detectUserLanguage(),
            familyContext: 'individual',
            greetingStyle: 'informal'
          }}
          onInteractionComplete={(transcription, response, emotion) => {
            // Add to chat history
            addToChatHistory({
              type: 'voice',
              user: transcription,
              assistant: response,
              emotion: emotion.primaryEmotion,
              timestamp: new Date()
            });
          }}
        />
      </div>
    </div>
  );
}
```

## Cultural Context Configuration

### Language Support
```tsx
const culturalContext = {
  language: 'hi-IN',      // Hindi (India)
  // language: 'en-US',   // English (US)  
  // language: 'ta-IN',   // Tamil (India)
  // language: 'te-IN',   // Telugu (India)
  
  familyContext: 'family-aware',    // Respects family dynamics
  greetingStyle: 'traditional'      // Traditional respectful greeting
};
```

### Family Context Options
- **`individual`**: Direct, personal mental health support
- **`family-aware`**: Considers family sensitivities in responses
- **`elder-present`**: Formal, respectful tone with elder consideration

### Greeting Styles
- **`informal`**: Casual, friendly approach
- **`formal`**: Professional, respectful interaction
- **`traditional`**: Cultural greetings with traditional values

## Crisis Detection & Safety

### Automatic Crisis Detection
```tsx
<VoiceCompanion
  crisisThreshold={0.7}  // Trigger at 70% stress level
  onCrisisDetected={(score, actions) => {
    // Emergency response protocol
    if (score > 0.8) {
      triggerEmergencyAlert();
      showTeleManasContact();
    }
    
    // Log for follow-up
    logCrisisIncident(score, actions);
  }}
/>
```

### Crisis Response Flow
1. **Real-time monitoring** during voice analysis
2. **Threshold detection** based on emotion + voice characteristics  
3. **Immediate escalation** with Tele MANAS contact (14416)
4. **Follow-up logging** for mental health professionals
5. **Family notification** (if family-aware context enabled)

## Advanced Features

### Emotion Analysis Display
```tsx
// Automatically shows emotion analysis with:
{
  primaryEmotion: 'anxious',
  confidence: 0.85,
  stressLevel: 0.6,
  characteristics: {
    pitch: 78,    // Higher pitch indicates stress
    volume: 45,   // Low volume may indicate withdrawal
    speed: 120,   // Fast speech indicates anxiety
    clarity: 92   // Clear speech indicates engagement
  }
}
```

### Session Management
```tsx
// Automatic conversation context preservation
const {
  conversationId,     // Track across sessions
  sessionId,          // Current voice session
  messageCount        // Total interactions
} = voiceCompanionData;
```

### Interruption Handling
- **Playback interruption**: User can speak while AI is responding
- **Recording override**: New recording stops previous playback
- **Error recovery**: Graceful handling of network/audio failures
- **State consistency**: Always returns to ready state

## Props Reference

### VoiceCompanionProps

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `authToken` | `string?` | - | Authentication token for API calls |
| `culturalContext` | `CulturalContext?` | - | Language and cultural settings |
| `crisisThreshold` | `number` | `0.7` | Crisis detection threshold (0-1) |
| `onCrisisDetected` | `function?` | - | Crisis detection callback |
| `onInteractionComplete` | `function?` | - | Interaction completion callback |
| `chatPaneMode` | `boolean` | `false` | Enable ChatPane integration styling |
| `showAdvancedControls` | `boolean` | `true` | Show detailed controls and info |
| `className` | `string` | `''` | Custom CSS classes |
| `disabled` | `boolean` | `false` | Disable entire component |

### CulturalContext

```tsx
interface CulturalContext {
  language: VoiceLanguageCode;           // Primary language
  familyContext: 'individual' | 'family-aware' | 'elder-present';
  greetingStyle: 'formal' | 'informal' | 'traditional';
}
```

## Backend Requirements

### Required Endpoints

The VoiceCompanion requires these backend endpoints to be available:

#### `/api/v1/voice/pipeline/audio` (POST)
- **Purpose**: Complete voice processing pipeline
- **Input**: FormData with audio file
- **Output**: Transcription, AI response, emotion analysis, TTS audio

```tsx
// Expected response format
{
  transcription: {
    text: string,
    language: string,
    confidence: number
  },
  aiResponse: {
    text: string,
    crisisScore: number,
    suggestedActions: string[],
    culturalAdaptations: any
  },
  emotion: {
    primaryEmotion: string,
    confidence: number,
    stressLevel: number,
    characteristics: {
      pitch: number,
      volume: number,
      speed: number,
      clarity: number
    }
  },
  ttsAudio: {
    blob?: Blob,
    url?: string,
    duration: number
  }
}
```

## Styling & Theming

### CSS Classes
```css
/* Main component styling */
.voice-companion {
  /* Base styles */
}

.voice-companion.chat-pane-mode {
  /* ChatPane integration styles */
}

.voice-companion.standalone-mode {
  /* Standalone component styles */
}

/* State-specific styling */
.voice-companion .recording-active {
  /* Recording state */
}

.voice-companion .processing-active {
  /* Processing state */
}

.voice-companion .playing-active {
  /* Playback state */
}

.voice-companion .crisis-detected {
  /* Crisis alert styling */
}
```

### Dark Mode Support
All components include dark mode support via Tailwind's `dark:` prefix classes.

## Error Handling

### Common Error Scenarios

1. **Microphone Permission Denied**
   - Graceful fallback to text input
   - Clear instructions for enabling permissions

2. **Network Connectivity Issues**
   - Retry mechanism with exponential backoff
   - Offline mode with cached responses

3. **Audio Processing Failures**
   - Fallback to simpler audio formats
   - Clear error messages for users

4. **Backend API Errors**
   - 3-tier fallback: RAG → Basic AI → Emergency resources
   - Always provide mental health support contact

### Error Recovery
```tsx
<VoiceCompanion
  onError={(errorType, message, details) => {
    console.error('Voice error:', { errorType, message, details });
    
    // Show user-friendly error message
    showErrorNotification(message);
    
    // Log for debugging
    logError('voice-companion', errorType, details);
    
    // Fallback to text input if voice fails
    if (errorType === 'microphone-permission') {
      enableTextFallback();
    }
  }}
/>
```

## Testing

### Unit Tests
```bash
# Test all voice components
npm test -- components/voice

# Test specific component
npm test -- VoiceCompanion.test.tsx
```

### Integration Tests
```bash
# Test with real backend (requires GCP credentials)
npm test -- voice-integration.test.ts
```

### Manual Testing Checklist

- [ ] **Recording**: Push-to-talk starts/stops recording
- [ ] **Permissions**: Microphone permission handling
- [ ] **Upload**: Audio file uploads to backend successfully
- [ ] **Processing**: Shows processing states clearly
- [ ] **Playback**: TTS audio plays automatically
- [ ] **Interruption**: Can interrupt playback with new recording
- [ ] **Errors**: Graceful error handling and recovery
- [ ] **Crisis**: Crisis detection triggers alerts
- [ ] **Cultural**: Hindi/English responses work correctly
- [ ] **Accessibility**: Screen reader announcements work

## Troubleshooting

### Common Issues

**Audio not recording:**
- Check microphone permissions in browser
- Verify HTTPS connection (required for MediaRecorder)
- Test with different audio formats

**Backend connection fails:**
- Verify `/api/v1/voice/pipeline/audio` endpoint is available
- Check authentication token validity
- Confirm CORS settings allow audio uploads

**Crisis detection not working:**
- Verify `crisisThreshold` is set appropriately
- Check emotion analysis is returning valid data
- Confirm `onCrisisDetected` callback is implemented

**Cultural context not applied:**
- Verify `culturalContext` prop is properly structured
- Check language detection is working
- Confirm backend supports specified language

## Performance Considerations

### Audio Processing
- **File size optimization**: Use compressed audio formats
- **Streaming**: Consider streaming for long recordings
- **Caching**: Cache TTS responses for common phrases

### Memory Management
- **Blob cleanup**: Automatically clean up audio blobs
- **Session limits**: Limit conversation history size
- **Component unmounting**: Proper cleanup on component unmount

### Network Optimization
- **Request batching**: Batch multiple audio requests
- **Retry logic**: Implement exponential backoff
- **Progress tracking**: Show upload/processing progress

---

## Support

For technical support or feature requests related to VoiceCompanion:

- **Documentation**: See `frontend/components/voice/README.md`
- **Crisis Support**: Tele MANAS 14416 (24/7)
- **Technical Issues**: Create GitHub issue with voice-companion label

The VoiceCompanion component represents the complete voice interaction experience for MITRA Sense, combining advanced AI with cultural sensitivity and crisis safety protocols.