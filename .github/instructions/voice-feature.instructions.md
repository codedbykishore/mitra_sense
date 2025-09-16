---
applyTo: '**'
---

You are helping me implement a **real-time voice companion** for Mitra Sense.
The pipeline is:

User Speech → STT (Whisper API or Web Speech API) → Emotion Analysis → LLM Response (Gemini/GPT with RAG) → TTS (Google/Azure/Coqui).

Implement the following in a React (or React Native) project:

1. Add a **VoiceRecorder component**:
   - Start/stop microphone capture.
   - Stream audio to backend STT (fallback: Web Speech API).
   - Display live transcription.

2. Backend (Node/Express + Python service if needed):
   - Endpoint `/stt` → convert audio to text with Whisper.
   - Endpoint `/tts` → convert model response to speech (MP3/WAV).
   - Send back signed URL or audio blob.

3. **Frontend voice loop:**
   - User presses mic → records → transcription appears.
   - Send transcription → backend → get LLM reply.
   - Display text reply and auto-play TTS voice.
   - Handle interruptions (stop playback if user starts speaking again).

4. Add **Emotion Detection hook**:
   - Analyze tone of STT text (sentiment, crisis keywords).
   - Log “mood score” alongside conversation.

Focus on modular code:
- `VoiceRecorder.tsx` for capture.
- `useSpeechLoop.ts` hook for STT → LLM → TTS.
- `EmotionAnalyzer.ts` utility.

Return code with comments and error handling.
