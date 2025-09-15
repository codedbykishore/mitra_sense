# MITRA - Mental Health Intelligence Through Responsive AI

This is a **full-stack Python FastAPI + React TypeScript application** for culturally-aware mental health support for Indian youth, using Google Cloud Vertex AI RAG Engine, Gemini 2.0 Flash, and Firestore.

## Essential Development Patterns

### Configuration & Environment Setup

**Critical**: The `secrets/google-credentials.json` file (NOT `secrets.json`) contains GCP service account credentials. The `app/config.py` uses a custom pattern to load both env vars and JSON credentials:

```python
# Always export this before running anything
export GOOGLE_APPLICATION_CREDENTIALS="secrets/google-credentials.json" 

# Run backend
uvicorn app.main:app --reload  # FastAPI at localhost:8000

# Run frontend
cd frontend && npm run dev     # Vite at localhost:5173
```

### Service Layer Architecture

**All services follow async patterns** - never create sync methods in services. Example from `GeminiService`:

```python
# ✅ Correct pattern
async def process_cultural_conversation(self, message: str, language: str) -> Dict:
    
# ❌ Avoid sync methods in services  
def process_message(self, message: str) -> Dict:
```

**3-tier fallback system**: RAG → basic AI → emergency response. Every AI interaction must have fallback logic.

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

### API Route Patterns

Routes are organized by domain in `app/routes/`. Each router follows this pattern:

```python
# app/routes/domain.py
from fastapi import APIRouter, Depends
from app.models.schemas import DomainRequest, DomainResponse

router = APIRouter()

@router.post("/endpoint", response_model=DomainResponse)
async def endpoint_handler(request: DomainRequest):
    # Always async, always use Pydantic models
```

Register in `app/main.py`: `app.include_router(router, prefix="/api/v1/domain")`

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
export GOOGLE_APPLICATION_CREDENTIALS="secrets/google-credentials.json"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run backend (FastAPI auto-reloads)
uvicorn app.main:app --reload  # localhost:8000

# 4. Run frontend in separate terminal  
cd frontend && npm install && npm run dev  # localhost:5173
```

### Testing Workflow

**Different test types require different setup**:

```bash
# Unit tests (no GCP required) - fastest
python -m pytest -qvs -m "not integration" 

# Integration tests (need real GCP) - for service validation
python -m pytest -qvs -m integration

# Specific service testing
python -m pytest -qvs tests/test_gemini_ai.py
```

### API Testing Pattern

The app uses `/api/v1` prefix for all endpoints:

```bash
# Test chat with cultural context
curl -X POST http://localhost:8000/api/v1/input/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mann nahi lag raha padhai mein"}'

# Crisis detection
curl -X POST http://localhost:8000/api/v1/crisis/detect \
  -H "Content-Type: application/json" \
  -d '{"message": "Sab kuch khatam ho gaya hai"}'
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

## Key API Endpoints & Routing Patterns

**All endpoints use `/api/v1` prefix**. Routes organized by domain in `app/routes/`:

- **`/api/v1/input/chat`**: Main RAG-enhanced conversation endpoint
- **`/api/v1/crisis/detect`**: Crisis pattern detection and risk scoring
- **`/api/v1/voice/*`**: Complete speech processing pipeline  
- **`/api/v1/auth/*`**: Google OAuth + JWT session management

### CORS Configuration Pattern

Frontend-backend communication requires specific CORS setup in `main.py`:

```python
# CORS for React dev server
origins = [
    "http://localhost:5173",   # Vite React dev
    "http://127.0.0.1:5173",   # Alternative localhost
]

app.add_middleware(CORSMiddleware, allow_origins=origins, ...)
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

## Configuration & Secrets Management

### Critical Files & Environment

**Actual filename**: `secrets/google-credentials.json` (not `secrets.json` as mentioned elsewhere)

```bash
# Required environment variables  
export GOOGLE_APPLICATION_CREDENTIALS="secrets/google-credentials.json"
GOOGLE_PROJECT_ID="auto-loaded-from-credentials"
CORPUS_NAME="projects/.../ragCorpora/..."  # RAG corpus identifier
SECRET_KEY="jwt-secret"
```

**Config pattern**: `app/config.py` loads both environment variables AND JSON credentials automatically:

```python
# Custom config loading - don't modify this pattern
def _load_google_config(self):
    cred_path = Path(self.GOOGLE_CREDENTIALS_FILE)  
    # Auto-extracts project_id and client_email from JSON
```

### Database Models & API Schemas

**Firestore models** (`app/models/db_models.py`): Document-based storage for users, conversations, crisis alerts

**API schemas** (`app/models/schemas.py`): Pydantic models with **strict validation**:

```python
# Use Field validation for all user inputs
message: str = Field(..., min_length=1, max_length=1024)
language: LanguageCode = Field(default=LanguageCode.ENGLISH_US)
```

**Always use Enums** for fixed values like language codes, never raw strings.

## Implementation Status & Key Files

### ✅ Core Features Implemented

- **Chat System**: `app/routes/input.py` - RAG-enhanced conversations
- **Crisis Detection**: `app/routes/crisis.py` + `app/services/crisis_service.py`  
- **Voice Pipeline**: `app/routes/voice.py` + `app/services/google_speech.py`
- **Authentication**: `app/routes/auth.py` with Google OAuth + JWT
- **AI Integration**: `app/services/gemini_ai.py` with Vertex AI RAG

### 🚧 Partially Implemented  

- **Family/Peer routes**: Route files exist but service logic incomplete
- **Analytics endpoints**: Health checks exist but comprehensive metrics pending

### Essential Dependencies

```python
# Core AI/ML stack
google-cloud-aiplatform==1.111.0  # Vertex AI integration
vertexai                          # Gemini model access  
langdetect==1.0.9                 # Language detection

# Backend framework
fastapi                           # Async API framework
pydantic-settings                 # Configuration management

# Frontend (in frontend/package.json)
react: "^19.1.1"                 # React 19 with TypeScript
vite: "^7.1.2"                   # Build tool
tailwindcss: "^4.1.12"          # Styling
```

## Development Guidelines

### Code Quality Standards

- **Type hints mandatory** on all function signatures
- **Async/await patterns** for all service methods  
- **Pydantic validation** for all API inputs/outputs
- **Error handling** with 3-tier fallbacks (RAG → basic AI → emergency)

### Cultural & Safety Requirements

- **Crisis safety**: Always escalate high-risk scenarios to Tele MANAS (14416)
- **Cultural sensitivity**: Test Hindi expressions and family dynamics
- **Privacy first**: Anonymous tracking, no PII storage
- **Accessibility**: Voice support for varying literacy levels

**Always provide context and explanation with code changes, never just raw code blocks.**
