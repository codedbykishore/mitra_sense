<div align="center">

# **MITRA Sense** 
### *Culturally Intelligent Mental Wellness Platform for Indian Youth*

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-blue?style=for-the-badge&logo=google-cloud)](https://cloud.google.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)

---

<div align="center">
  <img src="./extras/image.avif" alt="MITRA Sense Banner" width="300" height="200" style="border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);"/>
</div>

---

**Empowering Indian youth with culturally contextualized emotional support using AI-driven conversations, real-time crisis detection, and multilingual voice interaction.**

</div>

## 🧭 Overview
**MITRA Sense (Mental Intelligence Through Responsive AI)** is a **Google Cloud–powered mental wellness platform** built to provide **culturally contextualized emotional support** for Indian youth.  
It combines **Gemini 2.5 AI models**, **RAG-based reasoning**, **multilingual voice interaction**, and **real-time crisis detection** into one seamless ecosystem — fully private, anonymous, and scalable.

---

## 🧠 Core AI System

### **Primary AI Engine — Gemini 2.5 Flash**
- Model ID: `gemini-2.5-flash`
- Multimodal reasoning (text, audio, image)
- 1M-token context for long therapy-like conversations
- Deep cultural context and emotion recognition  
- Used for all chat, emotion guidance, and family education workflows

### **Low-Latency Engine — Gemini 2.5 Flash-Lite**
- Model ID: `gemini-2.5-flash-lite`
- Optimized for real-time classification, translation & sentiment analysis  
- Powers crisis detection and instant response loops  
- 75% cost optimization during off-peak hours

### **Advanced Reasoning Engine — Gemini 2.5 Pro**
- Model ID: `gemini-2.5-pro`
- Handles escalation, crisis intervention logic, and professional recommendations  
- Used only in high-risk contexts for safe, verified responses  

---

## 🗣️ Voice & Language Intelligence

### **Speech-to-Text**
- Converts Hindi, English, Tamil, Telugu, and mixed speech into text  
- Real-time streaming and emotion-tone preservation  
- Profanity filtering and diarization enabled  

### **Text-to-Speech**
- Generates culturally authentic, neural voices (93+ Indian dialects)  
- SSML-based emotional tone control  
- Used for empathetic and natural-sounding replies  

### **Translation**
- Supports all major Indian languages  
- Context-aware translation preserving cultural nuances  
- Enables cross-language peer support  

---

## 🧩 System Architecture

MITRA follows a modular, service-driven architecture:

```
Frontend (Next.js 14 + Tailwind)  ←→  FastAPI Backend  ←→  Google Cloud AI Services
                                         │
                                         ├── Gemini (2.5 Flash / Pro)
                                         ├── Speech & TTS APIs
                                         ├── Firestore / Storage
                                         └── Vertex AI RAG Engine
```

Each component communicates asynchronously via REST endpoints (`/api/v1/*`) ensuring scalability, low latency, and reliability.

---

## ⚙️ Core Backend Services

| Service | File | Description |
|----------|------|-------------|
| **GeminiService** | `app/services/gemini_ai.py` | Handles RAG-enhanced cultural conversations |
| **SpeechService** | `app/services/google_speech.py` | Manages multilingual voice processing |
| **RAGService** | `app/services/rag_service.py` | Retrieves knowledge from curated Indian wellness corpus |
| **FirestoreService** | `app/services/firestore.py` | Stores anonymous conversations and alerts |
| **CrisisService** | `app/services/crisis_service.py` | Detects risk patterns and escalates to Tele-MANAS |

All services follow strict async/await patterns with a **3-tier fallback system (RAG → Base AI → Crisis Escalation).**

---

## 💬 Voice Companion Architecture

From  :

```
🎤 User Audio → FastAPI STT → Emotion Analysis → Gemini + RAG → TTS → Playback 🎧
```

**Frontend Components:**
- `VoiceRecorder.tsx`: MediaRecorder capture
- `VoicePlayer.tsx`: Smooth playback with interruption handling
- `useSpeechLoop.ts`: Complete request/response loop
- `useEmotionTracking.ts`: Emotion scoring and visualization

**Backend Endpoints:**
- `/api/v1/voice/transcribe` — STT
- `/api/v1/voice/emotion` — Emotion scoring
- `/api/v1/voice/synthesize` — TTS synthesis
- `/api/v1/voice/pipeline/audio` — End-to-end audio → audio conversation

---

## 💻 Frontend Technology Stack

### **React + Next.js 14**
- Server-side rendering (fast startup)
- Progressive Web App (offline mode)
- Anonymous chat interface
- Voice input integration  
- Dynamic imports for hydration safety (`dynamic(..., { ssr: false })`)

### **Tailwind CSS**
- Indian-inspired design palette  
- RTL and dark-mode support  
- Fully WCAG-compliant UI  

### **Socket.IO**
- Real-time peer chat and voice room coordination  
- Typing indicators & connection management  

---

## 🔧 Backend Technology Stack

### **FastAPI**
- Async architecture for concurrent connections  
- OpenAPI documentation  
- Integrated validation via Pydantic models  

### **Core Libraries**
```python
google-cloud-aiplatform==1.111.0
google-cloud-speech==2.24.0
google-cloud-translate==3.15.0
google-cloud-firestore==2.16.0
fastapi[all]==0.104.1
pydantic==2.5.0
socketio==5.10.0
langdetect==1.0.9
```

---

## ☁️ Infrastructure on Google Cloud

- **Cloud Run** – Fully serverless FastAPI deployment  
- **Firestore** – Real-time encrypted storage  
- **Cloud Storage** – Audio files & cultural datasets  
- **Cloud KMS** – Secure key management  
- **VPC + IAM** – Private networking & anonymous authentication  
- **Vertex AI Evaluation** – Response safety & cultural scoring  

---

## 🧩 API Endpoints Summary

| Domain | Endpoint | Function |
|--------|-----------|----------|
| **Chat** | `/api/v1/input/chat` | RAG-enhanced conversation |
| **Voice** | `/api/v1/voice/pipeline/audio` | Complete voice loop |
| **Crisis** | `/api/v1/crisis/detect` | Detects high-risk patterns |
| **Peer Support** | `/api/v1/peer/match` | Anonymous peer matching |
| **Auth** | `/api/v1/auth/google` | Google OAuth sign-in |

---

## 💬 Cultural Intelligence & Crisis Handling

- Detects **Indian linguistic patterns** like “ghabrahat”, “mann nahi lagta”, “thakaan”  
- Automatically analyzes emotion tone (voice + text)
- Supports **mixed-language (Hinglish)** conversations  
- Crisis detection integrated with **Tele-MANAS (14416)**  
- Provides culturally contextual family guidance and coping strategies  

---

## 🛡️ Privacy, Safety & Compliance

- **No PII stored** — all interactions anonymous  
- **End-to-End Encryption** for voice & chat  
- **Audit Logging** for AI decisions  
- **Binary Authorization & Cloud Armor** for security  
- **HIPAA-aligned** infrastructure  
- **Regional Data Residency**: Indian user data stays in India  

---

## 🧪 Testing & CI/CD

```bash
# Run all tests
python -m pytest -qvs

# Integration only
python -m pytest -qvs -m integration

# Unit only
python -m pytest -qvs -m "not integration"
```

**Coverage:**
- AI service validation  
- Voice pipeline testing  
- Cultural & crisis detection accuracy  
- End-to-end chat flow verification  

---

## 🚀 Deployment & Scaling

**Local Setup**
```bash
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS="secrets/secrets.json"
uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

**Production**
- Docker-based containerization  
- Cloud Run auto-scaling (10,000+ concurrent users)  
- 99.9% uptime target  
- Off-peak pricing optimization  

---

## 🎯 Key Highlights

- Multimodal AI with **Gemini 2.5 Series**
- **RAG-enhanced cultural intelligence**
- Real-time **voice-first** conversations  
- Anonymous **peer support** matching  
- Integrated **Tele-MANAS** escalation  
- Culturally aware design for Indian mental health
- End-to-end **privacy & encryption**  
- Designed for **scale, reliability, and empathy**

---

## ⚖️ License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
