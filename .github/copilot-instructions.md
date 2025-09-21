# MITRA - Mental Health Intelligence Through Responsive AI

This is a **full-stack Python FastAPI + Next.js React TypeScript application** for culturally-aware mental health support for Indian youth, using Google Cloud Vertex AI RAG Engine, Gemini 2.0 Flash, and Firestore.

## Essential Development Patterns

### Configuration & Environment Setup

**Critical**: The `secrets/secrets.json` file contains GCP service account credentials. The `app/config.py` uses a custom pattern to load both env vars and JSON credentials:

```bash
# Always export this before running anything
export GOOGLE_APPLICATION_CREDENTIALS="secrets/secrets.json" 

# Run backend
uvicorn app.main:app --reload  # FastAPI at localhost:8000

# Run frontend  
cd frontend && npm run dev     # Next.js at localhost:3000
```

**Frontend Architecture**: Next.js 14+ with App Router, not Vite. API calls proxied via `next.config.mjs` rewrites to backend.

### Service Layer Architecture

**All services follow async patterns** - never create sync methods in services. Example from `GeminiService`:

```python
# ✅ Correct pattern
async def process_cultural_conversation(self, message: str, language: str) -> Dict:
    
# ❌ Avoid sync methods in services  
def process_message(self, message: str) -> Dict:
```

**3-tier fallback system**: RAG → basic AI → emergency response. Every AI interaction must have fallback logic.

### Frontend Hydration Patterns

**Critical for Next.js SSR**: Use `dynamic()` imports with `ssr: false` for client-only components:

```typescript
// Components using browser APIs (MediaRecorder, localStorage, etc.)
const VoiceCompanion = dynamic(() => import('./voice/VoiceCompanion'), {
  ssr: false,
  loading: () => <LoadingSpinner />
});

// Add suppressHydrationWarning for elements modified by extensions/themes
<html suppressHydrationWarning={true}>
<body suppressHydrationWarning={true}>
```

### Voice Processing Architecture

**Complete file-based pipeline** (`frontend/components/voice/`):

```typescript
// File upload workflow: Record → Upload → AI Process → TTS → Playback
const response = await fetch('/api/v1/voice/pipeline/audio', {
  method: 'POST',
  body: formData  // Contains audio file + metadata
});

// Expected response structure matches VoicePipelineResponse interface
const result = await response.json(); // transcription, emotion, aiResponse, ttsAudio
```

### Testing Strategy

Use pytest markers for different test categories:

```bash
# Run all tests
python -m pytest -qvs

# Integration tests only (require real GCP credentials)  
python -m pytest -qvs -m integration

# Unit tests only (mocked dependencies)
python -m pytest -qvs -m "not integration"
```

**Critical**: Integration tests in files like `test_*_real.py` require actual GCP setup. Unit tests mock all external dependencies.

## Core Service Dependencies & Integration Points

### GeminiService (`app/services/gemini_ai.py`)

**The main AI orchestrator** - handles RAG-enabled conversations with cultural context:

```python
# Initialize with RAG corpus
gemini_service = GeminiService(rag_corpus_name=settings.CORPUS_NAME)

# Cultural conversation processing
response = await gemini_service.process_cultural_conversation(
    message="Bohot ghabrahat ho rahi hai", 
    language="hi-IN"
)
```

**Key methods**: `process_cultural_conversation()`, `detect_crisis_patterns()`, `generate_family_education()`

### Voice Pipeline Integration (`app/routes/voice.py`)

**Complete audio processing workflow**:

```python
# Single endpoint handles entire voice pipeline
@router.post("/voice/pipeline/audio")
async def voice_pipeline_json(audio: UploadFile, ...):
    # STT → Emotion Analysis → Gemini AI → TTS → JSON Response
    return {
        "transcription": {...},
        "emotion": {...}, 
        "aiResponse": {...},
        "ttsAudio": {"url": "data:audio/mpeg;base64,..."} # Data URL format
    }
```

### Language Detection Pattern

Uses `langdetect` with consistent seeding. **Always handle LangDetectException**:

```python
from langdetect import detect, LangDetectException, DetectorFactory
DetectorFactory.seed = 0  # Consistent results

try:
    language = detect(message)
except LangDetectException:
    language = "en"  # Fallback to English
```

### Pydantic Schema Conventions

All API models in `app/models/schemas.py` use **strict typing and validation**:

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1024)
    language: LanguageCode = Field(default=LanguageCode.ENGLISH_US)
    cultural_context: Dict[str, str] = Field(default_factory=dict)
```

**Use Enums for fixed values** like `LanguageCode` instead of raw strings.

## Critical Developer Workflows

### Environment Setup (MUST DO FIRST)

```bash
# 1. Set up GCP credentials - actual filename in secrets/
export GOOGLE_APPLICATION_CREDENTIALS="secrets/secrets.json"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run backend (FastAPI auto-reloads)
uvicorn app.main:app --reload  # localhost:8000

# 4. Run frontend in separate terminal  
cd frontend && npm install && npm run dev  # localhost:3000
```

### Frontend Development Patterns

**Next.js App Router structure** in `frontend/app/`:

```typescript
// layout.tsx - Root layout with Analytics and theme handling
// page.tsx - Main page with dynamic imports for hydration safety
// globals.css - Tailwind CSS setup
```

**Component patterns** (`frontend/components/`):
- `AIAssistantUI.jsx` - Main app container with client-side state management
- `ChatPane.jsx` - Chat interface with integrated VoiceCompanion
- `voice/` - Complete voice interaction system

### API Testing Pattern

The app uses `/api/v1` prefix for all endpoints:

```bash
# Test chat with cultural context
curl -X POST http://localhost:8000/api/v1/input/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mann nahi lag raha padhai mein"}'

# Voice pipeline testing
curl -X POST http://localhost:8000/api/v1/voice/pipeline/audio \
  -F "audio=@test.webm" \
  -F "duration=5.0"
```

## Cultural Intelligence & Mental Health Patterns

### Understanding the Domain Context

**This is NOT a generic chatbot** - MITRA specializes in:

1. **Indian Cultural Expressions**: "ghabrahat" (anxiety), "mann nahi lagta" (not feeling like it), "pareshaan" (troubled)
2. **Crisis Patterns**: Multi-level risk assessment with automatic Tele MANAS (14416) escalation  
3. **Family Dynamics**: Respects traditional values while supporting individual mental health
4. **Language Mixing**: Hindi-English code-switching in conversations

### Crisis Detection Logic

**Every AI response includes crisis scoring**. Pattern from `ChatResponse` schema:

```python
class ChatResponse(BaseModel):
    response: str
    crisis_score: float = 0.0  # 0-1 scale, >0.7 triggers escalation
    suggested_actions: List[str] = Field(default_factory=list)
```

**Safety-first approach**: When in doubt, escalate to professional resources.

### RAG Knowledge Base Structure

The `rag_data/mitra_knowledge_base.jsonl` contains 600+ culturally-curated resources. RAG responses should **always include sources**:

```python
class ChatResponse(BaseModel):
    rag_sources: List[str] = Field(default_factory=list)  # Track knowledge sources
    cultural_adaptations: Dict[str, str] = Field(default_factory=dict)
```

### Voice Processing Pipeline

Complete audio → text → AI → audio pipeline for accessibility:

1. **Speech-to-Text**: Supports Hindi, English, Tamil, Telugu
2. **Cultural Context**: Maintains meaning across language detection  
3. **Text-to-Speech**: Generates culturally-appropriate voice responses
4. **File-based Workflow**: MediaRecorder → FormData → Backend → Data URL TTS

## Key API Endpoints & Routing Patterns

**All endpoints use `/api/v1` prefix**. Routes organized by domain in `app/routes/`:

- **`/api/v1/input/chat`**: Main RAG-enhanced conversation endpoint
- **`/api/v1/crisis/detect`**: Crisis pattern detection and risk scoring
- **`/api/v1/voice/pipeline/audio`**: Complete voice processing pipeline (NEW)
- **`/api/v1/auth/*`**: Google OAuth + JWT session management

### Frontend-Backend Communication

**Next.js proxy setup** in `next.config.mjs`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/v1/:path*',
      destination: 'http://localhost:8000/api/v1/:path*',
    },
  ];
}
```

## Error Handling & Safety Patterns

### 3-Tier Fallback System

**Every AI interaction must handle failures gracefully**:

1. **RAG Response**: Try knowledge base retrieval first
2. **Basic AI**: Fall back to general Gemini without RAG  
3. **Emergency**: Static crisis resources and Tele MANAS contact

### Crisis Safety Requirements

**Never ignore crisis indicators**. Always include safety resources:

- Immediate escalation for crisis_score > 0.7
- Include Tele MANAS (14416) in all crisis responses
- Log all crisis detections for follow-up

## Implementation Status & Key Files

### ✅ Core Features Implemented

- **Chat System**: `app/routes/input.py` - RAG-enhanced conversations
- **Crisis Detection**: `app/routes/crisis.py` + `app/services/crisis_service.py`  
- **Voice Pipeline**: `app/routes/voice.py` + `app/services/google_speech.py` (COMPLETE)
- **Voice Frontend**: `frontend/components/voice/VoiceCompanion.tsx` (COMPLETE)
- **Authentication**: `app/routes/auth.py` with Google OAuth + JWT session management (COMPLETE)
- **User Onboarding Flow**: Complete student/institution onboarding system (COMPLETE)
- **Institution Management**: Global institutions collection with validation (COMPLETE)
- **AI Integration**: `app/services/gemini_ai.py` with Vertex AI RAG

### ✅ Authentication & User Management (COMPLETE)

- **Google OAuth Integration**: Full OAuth flow via `app/routes/auth.py`
  - `/google/login` - Initiates Google OAuth flow
  - `/auth/google/callback` - Handles OAuth callback and user creation
  - `/me` - Returns current user session info with onboarding status
  - `/logout` - Clears user session
- **Session Management**: Starlette sessions for persistent login state
- **User Dependencies**: `app/dependencies/auth.py` with `get_current_user_from_session()`
- **Frontend Auth Components**: `Login.jsx`, `Logout.jsx`, `useUser.ts` hook
- **Auto-redirect Logic**: New users → onboarding, existing users → main app

### ✅ User Onboarding System (COMPLETE)

- **Onboarding Frontend**: `frontend/app/onboarding/page.tsx`
  - Student role: Name, Age, Region, Language preference, Institution selection
  - Institution role: Institution name, Contact person, Region
  - Dynamic institution dropdown populated from Firestore
  - Form validation and error handling
  - Responsive Tailwind UI with loading states
- **Onboarding Backend**: `app/routes/users.py`
  - `/api/v1/users/onboarding` - Completes user onboarding
  - `/api/v1/users/profile` - Gets user profile and onboarding status
  - `/api/v1/users/institutions` - Lists all active institutions
- **Institution Persistence**: Global `institutions` collection in Firestore
  - Unique institution name validation
  - Student count tracking
  - Region-based organization
- **User Context Integration**: `useUser.tsx` tracks onboarding status and role

### ✅ Voice Integration System (COMPLETE)

- **Complete Voice Pipeline**: Record → Upload → AI Process → TTS → Playback
- **VoiceCompanion Integration**: Fully integrated into ChatPane with push-to-talk
- **Cultural Voice Support**: Hindi/English detection and TTS response
- **Crisis Detection**: Real-time voice emotion analysis with emergency escalation
- **Accessibility Features**: Screen reader support, keyboard navigation, ARIA labels
- **Error Recovery**: Comprehensive fallback system for all failure scenarios
- **Hydration Safety**: Client-side rendering with proper SSR compatibility

### ✅ Database & Firestore Integration (COMPLETE)

- **FirestoreService**: `app/services/firestore.py`
  - User CRUD operations with async patterns
  - Institution management with student count tracking
  - Conversation and message persistence
  - Crisis event logging for follow-up care
- **Data Models**: `app/models/db_models.py`
  - User model with onboarding fields (role, profile, institution_id)
  - Institution model with validation and tracking
  - Conversation and Message models for chat history
- **Schema Validation**: `app/models/schemas.py`
  - OnboardingRequest/Response with role-based validation
  - InstitutionsListResponse for frontend consumption
  - Comprehensive type safety with Pydantic

### ✅ Technical Achievements Completed

- **Next.js App Router Architecture**: Proper server/client component separation
- **Hydration Issue Resolution**: All SSR/client-side rendering conflicts resolved
- **API Proxy Configuration**: Complete Next.js → FastAPI proxy setup working
- **TypeScript Integration**: Full type safety across frontend and backend
- **Environment Configuration**: Development/production environment handling
- **Testing Infrastructure**: pytest with integration/unit test separation
- **Google Cloud Integration**: TTS, STT, Vertex AI RAG fully operational
- **Cultural Language Support**: Hindi/English code-switching detection
- **Crisis Safety Systems**: Multi-level risk assessment with Tele MANAS integration

### ✅ Comprehensive Testing Suite (NEW)

- **Authentication Tests**: `test_auth.py` (mocked) + `test_auth_real.py` (integration)
  - Google OAuth flow testing, JWT token validation, session management
  - Login/logout endpoints, user authentication dependencies
  - Password hashing and security utilities testing
- **Onboarding Tests**: `test_onboarding.py` (mocked) + `test_onboarding_real.py` (integration)
  - Student/institution role onboarding workflows
  - Institution selection and validation, profile completion
  - Onboarding status tracking and user redirect logic
- **Voice Pipeline Tests**: `test_voice_pipeline.py` (mocked) + `test_voice_pipeline_real.py` (integration)
  - Complete voice processing workflow (STT → AI → TTS)
  - Cultural voice processing, crisis detection via voice emotion
  - Audio format validation, error handling, and accessibility features
- **Institution Management Tests**: `test_institutions.py` (mocked) + `test_institutions_real.py` (integration)
  - Institution CRUD operations, uniqueness validation
  - Student count tracking, region-based filtering
  - Complete user-institution enrollment workflows
- **Testing Convention**: `_real.py` files test actual endpoints/Firestore, regular files use mocks
- **Pytest Markers**: `@pytest.mark.integration` for real tests requiring external services

### Essential Dependencies

```python
# Core AI/ML stack
google-cloud-aiplatform==1.111.0  # Vertex AI integration
vertexai                          # Gemini model access  
langdetect==1.0.9                 # Language detection
google-cloud-texttospeech         # TTS integration
google-cloud-speech               # STT integration

# Backend framework
fastapi                           # Async API framework
pydantic-settings                 # Configuration management
google-cloud-firestore           # Database operations
authlib                          # Google OAuth integration
python-jose[cryptography]        # JWT token handling
starlette                        # Session management

# Frontend (in frontend/package.json)
"next": "14.2.32"                # Next.js with App Router
"react": "^19.1.1"               # React 19 with TypeScript
"tailwindcss": "^4.1.12"        # Styling
"@radix-ui/react-*"             # Accessible UI components
```

## Development Guidelines

### Code Quality Standards

- **Type hints mandatory** on all function signatures
- **Async/await patterns** for all service methods  
- **Pydantic validation** for all API inputs/outputs
- **Error handling** with 3-tier fallbacks (RAG → basic AI → emergency)
- **Hydration safety** for all client-side components in Next.js

### Cultural & Safety Requirements

- **Crisis safety**: Always escalate high-risk scenarios to Tele MANAS (14416)
- **Cultural sensitivity**: Test Hindi expressions and family dynamics
- **Privacy first**: Anonymous tracking, no PII storage
- **Accessibility**: Voice support for varying literacy levels

**Always provide context and explanation with code changes, never just raw code blocks.**

## Terminal Guidelines

- Always source venv/bin/activate for Python environment
- Use `uvicorn app.main:app --reload` for backend with auto-reload
- Use `npm run dev` in `frontend/` for Next.js with hot-reload
- Do not export GOOGLE_APPLICATION_CREDENTIALS we already have it set in the environment
- Always cd into `frontend/` before running npm commands