# MITRA-Sense — GitHub Copilot Repository Instructions (Single Source of Truth)

## Purpose

- These are the **only instructions Copilot will automatically read** across the repository.  
- They apply to inline suggestions, Copilot Chat, and (where available) PR review.  
- Keep this file authoritative and up to date with PRD, schemas, and architecture.  

---

## Project Overview

- **MITRA (Mental Health Intelligence Through Responsive AI)** — culturally-aware mental wellness platform for Indian youth.  
- **Stack**:  
  - Backend: Python (FastAPI, Firestore, Vertex AI, Gemini 2.0 Flash, Speech APIs, RAG).  
  - Frontend: React 19 + TypeScript + Vite + Tailwind.  
- **Core Features**: RAG-enhanced chat, voice-first pipeline, crisis detection/escalation, peer and family support.  
- **Cultural Context**: Mixed Hindi/English, Indian family dynamics, crisis escalation via Tele MANAS (14416).  

---

## Authoritative References (open when prompting)

- `/ARCHITECTURE.md` — complete system and services spec.  
- `/app/models/schemas.py` — strict Pydantic request/response schemas.  
- `/rag_data/mitra_knowledge_base.jsonl` — cultural knowledge base for RAG.  
- `/tests/` — unit and integration test suites.  

---

## Global Safety & Compliance Rules

- **Async-only services** — never define sync methods under `/app/services/`.  
- **3-tier fallback required** for every AI call:  
  1. RAG →  
  2. Gemini-only →  
  3. Static emergency response.  
- **Crisis safety**:  
  - `crisis_score >= 0.7` → escalate immediately (≥0.8 in final deployment).  
  - Always include Tele MANAS (14416).  
- **Privacy-first**: No PII in Firestore, only anonymous sessions & conversations.  
- **Schemas mandatory**: All requests/responses must validate against Pydantic models.  
- **Enums > raw strings** for language codes, etc.  
- **No hardcoded secrets**: configs come from `secrets/secrets.json` + env vars.  
- **Structured logging**: JSON with timestamps + identifiers; no silent failures.  

---

## Testing & Validation (global expectations)

- **Unit tests**:  
  ```bash
  pytest -m "not integration"
  ```  
  (Mock external dependencies, no GCP calls).  
- **Integration tests**:  
  ```bash
  pytest -m integration
  ```  
  (Require real GCP credentials).  
- **Validation focus**:  
  - Crisis detection (English + Hindi expressions).  
  - RAG cultural retrieval accuracy.  
  - Voice pipeline correctness (STT → Emotion → Gemini → TTS).  

---

## Module Section — Backend (/app, FastAPI)

### Purpose
- Provide API endpoints, business logic, AI integrations, and crisis detection.

### Languages & Tools
- Python 3.11+, FastAPI, Pydantic, Firestore, Vertex AI, Google Speech.

### Core Requirements

1. **Gemini AI Service (`gemini_ai.py`)**
   - Must be async.  
   - Use RAG for knowledge retrieval.  
   - Return: `response`, `crisis_score`, `rag_sources`.  
   - Always include fallback tiers.  

2. **Voice Service (`google_speech.py`)**
   - Methods:  
     - `transcribe_audio(audio_data)` — multilingual STT.  
     - `detect_emotional_tone(audio_data)` — categorize `anxiety`, `sadness`, `anger`, `calmness`.  
     - `synthesize_response(text, language, cultural_tone)` — TTS with cultural tone.  
     - `process_voice_pipeline(audio_data)` — orchestrates full pipeline.  
   - Pipeline rule:  
     ```
     Audio → Language Detection → STT → Emotion → Gemini AI → Crisis Scoring → TTS
     ```  
   - Crisis override: if score ≥0.7, skip TTS, return emergency response only.  
   - Input formats: MP3, WAV, FLAC, M4A, OPUS, PCM, WebM.  
   - Output format: MP3 with cultural accent/intonation.  
   - **Implementation note**: Use file upload approach (not streaming) for reliability and complete context in crisis scenarios.  

3. **RAG Service (`rag_service.py`)**
   - Retrieve knowledge filtered by language/region.  
   - Always attach metadata + sources.  

4. **Firestore Service (`firestore.py`)**
   - Store users, conversations, crisis alerts.  
   - Anonymous IDs only — no PII.  

5. **Routes (`/app/routes/`)**
   - Organized by domain (input, crisis, voice, auth, family, peer).  
   - All prefixed `/api/v1/*`.  
   - Always async + Pydantic schema enforced.  

---

## Module Section — Frontend (/frontend, React + Vite)

### Purpose
- Provide intuitive, voice-first UI for chat, crisis detection, peer/family features.

### Language & Framework
- React 19 + TypeScript + Vite + Tailwind.

### Views & Interactions

1. **Chat**
   - Connect to `/api/v1/input/chat`.  
   - Display Gemini + RAG responses with cultural tone.  

2. **Voice**
   - Integrate mic → `/api/v1/voice/pipeline`.  
   - Show transcript, emotional analysis, and audio output.  
   - If `crisis_score >= 0.7`, block normal flow → show crisis escalation screen with Tele MANAS info.  
   - **File-based approach**: Record → upload → process → return audio response (not real-time streaming).  

3. **Family Support**
   - Pages for culturally-relevant education resources.  
   - Display coping guides & family communication tips.  

4. **Peer Support**
   - Anonymous peer matching (service logic partial).  
   - Show disclaimers about privacy & safety.  

---

## Module Section — Crisis Safety

- **Multilingual crisis detection**: both English and Hindi keywords (e.g., “end it all”, “मरना चाहता हूं”).  
- **Risk Scoring**: 0.0–1.0 scale.  
- **Escalation Path**:  
  1. Create `CrisisAlert` in Firestore.  
  2. Notify Tele MANAS (14416).  
  3. Provide coping resources (static text).  
  4. Offer peer connection (optional).  
  5. Notify family if consent exists.  

---

## Prompts & How To Use Copilot

### Reusable Chat Prompts
- **Backend**:  
  “Scaffold an async FastAPI route in `/app/routes/voice.py` with Pydantic schema validation.”  
- **Frontend**:  
  “Generate a React component for voice chat integrating `/api/v1/voice/pipeline` with Tailwind styling.”  
- **Crisis Testing**:  
  “Write pytest cases for crisis detection with mixed Hindi/English text.”  

### Good Prompting Habits
- Keep `/ARCHITECTURE.md` and `/app/models/schemas.py` open.  
- Request **small, testable increments** (one method/route at a time).  
- Restate **fallback rules** and **crisis thresholds** in prompts.  
- **Voice development**: Focus on file upload endpoints over streaming for faster implementation.  

### Verification
- In Copilot Chat, ask:  
  “Which repository instructions are active for this file?”  
- Copilot should list: `.github/copilot-instructions.md`.  

---

## Maintenance

- Update this file whenever schemas, architecture, or crisis rules change.  
- Reject Copilot suggestions that:  
  - Add sync methods in services,  
  - Skip fallback logic,  
  - Ignore crisis escalation,  
  - Store PII.  
- This file is the **single source of truth** for Copilot.  

---

