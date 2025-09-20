# Voice Companion Implementation

This directory contains the complete file-based voice interaction system for MITRA Sense mental health platform.

## 📁 Components Overview

### Core Components

#### 1. `VoiceRecorder.tsx`
**File-based push-to-talk audio recording component**
- MediaRecorder API integration with browser compatibility
- Visual recording states (idle, recording, processing, error)
- Microphone permission handling
- Duration limits with progress indication
- Audio blob export for backend upload
- Accessibility and error handling

```typescript
import { VoiceRecorder } from '@/components/voice';

<VoiceRecorder
  onRecordingComplete={(audioBlob, duration) => {
    // Handle recorded audio blob
  }}
  onError={(error, message) => {
    // Handle recording errors
  }}
  maxDuration={180} // 3 minutes
/>
```

#### 2. `VoiceCompanion.tsx`
**Complete voice interaction interface**
- Integrates VoiceRecorder with useSpeechLoop
- Real-time emotion analysis display
- Crisis detection and safety features
- Cultural context awareness (Hindi/English)
- Conversation history management
- Emergency contact integration (Tele MANAS)

```typescript
import { VoiceCompanion } from '@/components/voice';

<VoiceCompanion
  authToken="your-auth-token"
  culturalContext={{
    language: 'hi-IN',
    familyContext: 'family-aware',
    greetingStyle: 'traditional'
  }}
  onCrisisDetected={(score, actions) => {
    // Handle crisis situations
  }}
/>
```

### Hooks

#### 3. `useSpeechLoop.ts`
**Complete voice interaction workflow management**
- Audio upload to `/api/v1/voice/pipeline/audio`
- Backend response processing (STT, emotion, AI, TTS)
- Audio playback with interruption handling
- Conversation context management
- Error handling and recovery
- Session management

```typescript
import { useSpeechLoop } from '@/hooks/useSpeechLoop';

const {
  state,
  isRecording,
  isProcessing,
  isPlaying,
  error,
  currentTranscription,
  currentResponse,
  currentEmotion,
  processAudioBlob,
  cancelCurrent,
  resetSession
} = useSpeechLoop({
  authToken: 'your-token',
  culturalContext: { language: 'hi-IN' },
  autoPlayResponses: true
});
```

### Types & Utilities

#### 4. `types.ts`
**Comprehensive TypeScript definitions**
- Voice recording and playback states
- Error types for all scenarios
- Cultural context interfaces
- Emotion analysis structures
- Backend API response types
- Audio configuration options

#### 5. `VoiceRecorderDemo.tsx`
**Development and testing component**
- Complete usage example
- Audio playback testing
- Download functionality
- Technical details display

## 🔄 Complete Voice Interaction Flow

### 1. User Interaction
```
User presses microphone → Recording starts → Visual feedback
```

### 2. Audio Capture
```
MediaRecorder captures audio → Blob creation → Duration tracking
```

### 3. Backend Processing
```
FormData upload → /api/v1/voice/pipeline/audio → STT + Emotion + AI + TTS
```

### 4. Response Handling
```
Backend response → Transcription display → TTS audio playback
```

### 5. Conversation Management
```
Context preservation → Session tracking → History management
```

## 🎯 Key Features

### ✅ File-Based Recording
- Push-to-talk interface with visual feedback
- Audio blob generation ready for upload
- Duration limits and progress tracking
- Error handling for all scenarios

### ✅ Complete Backend Integration
- `/api/v1/voice/pipeline/audio` endpoint integration
- FormData upload with metadata
- Timeout and cancellation handling
- Response processing and display

### ✅ Audio Playback & Control
- Automatic TTS response playback
- Interruption handling (stop on new recording)
- Manual playback controls
- Audio error recovery

### ✅ Cultural Sensitivity
- Hindi/English language support
- Cultural context preservation
- Traditional greeting patterns
- Family-aware responses

### ✅ Mental Health Features
- Real-time emotion analysis
- Crisis detection and scoring
- Safety resource integration
- Tele MANAS emergency contact
- Mood tracking and visualization

### ✅ Accessibility
- ARIA labels and screen reader support
- Visual feedback for all audio states
- Keyboard navigation
- High contrast compatibility

## 🔧 Backend API Integration

### Expected Backend Response Format
```typescript
interface VoicePipelineResponse {
  transcription: {
    text: string;
    language: string;
    confidence: number;
  };
  
  emotion: {
    primaryEmotion: string;
    confidence: number;
    emotions: Record<string, number>;
    stressLevel: number;
  };
  
  aiResponse: {
    text: string;
    crisisScore: number;
    culturalAdaptations: Record<string, string>;
    suggestedActions: string[];
    ragSources?: string[];
  };
  
  ttsAudio: {
    url?: string;
    blob?: Blob;
    format: string;
    duration: number;
  };
  
  session: {
    sessionId: string;
    conversationId: string;
    timestamp: string;
  };
}
```

### Required Backend Endpoints
- `POST /api/v1/voice/pipeline/audio` - Complete voice processing pipeline
- Authentication via Bearer token
- FormData support for audio file upload

## 🚀 Usage Examples

### Basic Integration
```typescript
import { VoiceCompanion } from '@/components/voice';

function MyApp() {
  return (
    <VoiceCompanion
      authToken={user.token}
      culturalContext={{
        language: 'hi-IN',
        familyContext: 'individual',
        greetingStyle: 'informal'
      }}
      onCrisisDetected={(score, actions) => {
        if (score > 0.7) {
          // Show emergency contacts
          showEmergencyModal();
        }
      }}
    />
  );
}
```

### Advanced Hook Usage
```typescript
import { useSpeechLoop } from '@/hooks/useSpeechLoop';
import { VoiceRecorder } from '@/components/voice';

function CustomVoiceInterface() {
  const {
    processAudioBlob,
    currentResponse,
    currentEmotion,
    isProcessing,
    error
  } = useSpeechLoop({
    onInteractionComplete: (response) => {
      // Custom response handling
      console.log('Transcription:', response.transcription.text);
      console.log('Emotion:', response.emotion.primaryEmotion);
      console.log('AI Response:', response.aiResponse.text);
    }
  });

  return (
    <div>
      <VoiceRecorder
        onRecordingComplete={processAudioBlob}
        disabled={isProcessing}
      />
      
      {currentResponse && (
        <div>AI Response: {currentResponse}</div>
      )}
      
      {currentEmotion && (
        <div>Detected Emotion: {currentEmotion.primaryEmotion}</div>
      )}
    </div>
  );
}
```

## 🔒 Security & Privacy

### Audio Data Handling
- Audio blobs processed in memory
- No persistent local storage of recordings
- Secure HTTPS upload to backend
- Token-based authentication

### Mental Health Compliance
- Crisis detection with automatic escalation
- Emergency contact integration
- Anonymous session tracking
- Privacy-first approach

## 🧪 Testing

### Component Testing
```bash
# Test individual components
npm test VoiceRecorder.test.tsx
npm test useSpeechLoop.test.ts
npm test VoiceCompanion.test.tsx
```

### Integration Testing
```bash
# Test complete voice workflow
npm test voice-integration.test.ts
```

### Manual Testing
- Use VoiceRecorderDemo component for development
- Test with various audio formats and durations
- Verify cultural context handling
- Test crisis detection scenarios

## 📱 Browser Compatibility

### Supported Browsers
- ✅ Chrome 66+ (full support)
- ✅ Firefox 29+ (full support)
- ✅ Safari 14.1+ (full support)
- ✅ Edge 79+ (full support)

### Audio Format Support
- Primary: WebM with Opus codec
- Fallback: WebM, MP4, OGG, WAV
- Automatic format detection and selection

## 🔄 Future Enhancements

### Planned Features
- [ ] Real-time streaming audio (future upgrade from file-based)
- [ ] Multiple language TTS voices
- [ ] Advanced emotion visualization
- [ ] Voice authentication
- [ ] Offline mode support
- [ ] WebRTC integration for peer support

### Performance Optimizations
- [ ] Audio compression before upload
- [ ] Caching for repeated TTS responses
- [ ] Connection pooling for API calls
- [ ] Progressive audio loading

## 📖 Documentation

- [Voice Recording Guide](./docs/recording.md)
- [Backend Integration](./docs/backend.md)
- [Cultural Adaptation](./docs/cultural.md)
- [Accessibility Features](./docs/accessibility.md)
- [Crisis Handling Protocol](./docs/crisis.md)

## 🤝 Contributing

When working with voice components:

1. **Test with real audio devices**
2. **Verify cultural context handling**
3. **Test crisis detection scenarios**
4. **Ensure accessibility compliance**
5. **Update TypeScript types when needed**

---

**Note**: This implementation provides a complete file-based voice interaction system ready for production use in the MITRA Sense mental health platform.