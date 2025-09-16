---
applyTo: '**'
---

# Voice Companion Implementation Guide for MITRA Sense

You are implementing a **file-based voice companion** for MITRA's mental health platform.

## Current Architecture Context
- **Backend**: Python FastAPI with existing voice endpoints (`/api/v1/voice/*`)
- **Frontend**: Next.js React with TypeScript 
- **STT/TTS**: Google Cloud Speech services (already configured)
- **AI**: Gemini 2.0 Flash with RAG capabilities
- **Voice Pipeline**: Existing `/voice/pipeline` and `/voice/pipeline/audio` endpoints

## Implementation Pipeline
User Audio File → FastAPI STT → Emotion Analysis → Gemini Response + RAG → TTS Audio File → Frontend Playback

## Key Requirements

### 1. Leverage Existing Backend Infrastructure
- Use existing `/api/v1/voice/transcribe` for STT
- Use existing `/api/v1/voice/emotion` for emotion detection  
- Use existing `/api/v1/voice/synthesize` for TTS
- Use existing `/api/v1/voice/pipeline/audio` for complete flow

### 2. Frontend Voice Components (Next.js/React)
- **VoiceRecorder.tsx**: File-based audio capture with MediaRecorder API
- **VoicePlayer.tsx**: Audio playback with interruption handling
- **useSpeechLoop.ts**: Complete voice interaction hook
- **useEmotionTracking.ts**: Emotion analysis and mood logging

### 3. File-Based Voice Loop
- Push-to-talk → Record to Blob → Upload to FastAPI → Get response audio → Play
- Handle interruptions (stop playback when user speaks again)
- Error handling for network/audio issues
- Cultural context preservation throughout pipeline

### 4. Integration Points
- Integrate with existing chat UI (`ChatPane.jsx`)
- Use existing authentication (`useUser.jsx` hook)
- Maintain conversation context with RAG responses
- Log interactions for crisis detection

Focus on:
- **Modular architecture** following existing patterns
- **Cultural sensitivity** for Indian mental health context
- **Error handling** with 3-tier fallback (RAG → basic AI → crisis resources)
- **Accessibility** with visual feedback for audio states