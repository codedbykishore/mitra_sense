# MITRA - Mental Health Intelligence Through Responsive AI

This repo is a **full-stack Python FastAPI + React TypeScript application** for culturally-aware mental health support for Indian youth, using Google Cloud Vertex AI RAG Engine, Gemini 2.0 Flash, and Firestore.

## Project Architecture

```
├── app/                          # Backend FastAPI application
│   ├── main.py                   # FastAPI app entry point with all routes
│   ├── config.py                 # Settings and environment configuration
│   ├── core/
│   │   └── security.py           # Authentication and security utilities
│   ├── dependencies/
│   │   └── auth.py               # Dependency injection for auth
│   ├── models/
│   │   ├── db_models.py          # Firestore/database models
│   │   └── schemas.py            # Pydantic request/response models
│   ├── routes/                   # API endpoints organized by feature
│   │   ├── input.py              # Chat endpoints with RAG
│   │   ├── voice.py              # Voice processing pipeline
│   │   ├── crisis.py             # Crisis detection and intervention
│   │   ├── family.py             # Family education and guidance
│   │   ├── peer.py               # Peer support and matching
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── analytics.py          # Usage analytics and monitoring
│   │   └── rag.py                # RAG-specific endpoints
│   └── services/                 # Core business logic services
│       ├── gemini_ai.py          # Primary AI service with RAG integration
│       ├── google_speech.py      # Speech-to-text, TTS, emotion detection
│       ├── rag_service.py        # RAG implementation and knowledge retrieval
│       ├── firestore.py          # Firestore database operations
│       └── security.py           # Security and encryption services
├── frontend/                     # React TypeScript web application
│   ├── src/
│   │   ├── App.tsx               # Main React application
│   │   ├── components/
│   │   │   └── Chatbot.tsx       # Chat interface component
│   │   └── assets/               # Static assets
│   └── package.json              # Frontend dependencies (React, TypeScript, Tailwind)
├── tests/                        # Comprehensive test suite
│   ├── test_gemini_ai.py         # AI service tests
│   ├── test_google_speech.py     # Speech processing tests
│   ├── test_rag_*.py             # RAG system integration tests
│   ├── test_firestore_service.py # Database service tests
│   └── audio/                    # Test audio files for speech testing
├── rag_data/
│   └── mitra_knowledge_base.jsonl # 600+ cultural mental health resources
├── secrets/
│   └── secrets.json              # GCP service account credentials
└── resources/                    # Documentation and project resources
```

## Key Technologies & Dependencies

### Backend Stack

- **AI/ML**: Vertex AI RAG Engine, Gemini 2.0 Flash, Google Speech APIs
- **Framework**: FastAPI with async/await patterns
- **Database**: Google Firestore (NoSQL) for scalable user data
- **Authentication**: Custom JWT with security middleware
- **Cloud**: Google Cloud Platform (Vertex AI, Cloud Storage, Firestore)

### Frontend Stack

- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS for responsive design
- **Build**: Vite for fast development and building
- **Components**: Custom chat interface with voice support

### Languages Supported

- **Primary**: English, Hindi, Tamil, Telugu
- **Cultural Context**: Hindi expressions, Indian family dynamics

## How to Run & Test

### Backend Development

```bash
#Activate venv
source venv/bin/activate


# Run FastAPI development server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Run React development server
npm run dev

# Frontend will be available at http://localhost:5173
```

### Testing

```bash
# Run all backend tests
python -m pytest -vs tests/


# Test API endpoints
curl http://localhost:8000/api/v1/input/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Bohot ghabrahat ho rahi hai exams ke liye"}'
```

## Core Services & Architecture Patterns

### GeminiService (`app/services/gemini_ai.py`)

- **Primary AI orchestrator** using Vertex AI RAG Engine + Gemini 2.0
- **Cultural intelligence**: Understands Hindi expressions like "ghabrahat", "mann nahi lagta"
- **Crisis detection**: Multi-level risk assessment with automatic escalation
- **Key methods**: `process_cultural_conversation()`, `detect_crisis_patterns()`, `generate_family_education()`

### SpeechService (`app/services/google_speech.py`)

- **Multilingual voice processing** with emotion detection
- **Pipeline**: Audio input → Language detection → STT → AI processing → TTS → Audio output
- **Supported**: Hindi, English, Tamil, Telugu with cultural tone adaptation
- **Key methods**: `transcribe_audio()`, `synthesize_response()`, `process_voice_pipeline()`

### RAGService (`app/services/rag_service.py`)

- **Knowledge retrieval** from culturally-curated mental health database
- **Context-aware**: Filters content by cultural background, crisis level, language
- **Integration**: Works with Vertex AI Vector Search and embedding models

### FirestoreService (`app/services/firestore.py`)

- **Database operations** for user data, conversations, crisis alerts
- **Privacy-first**: Anonymous user tracking with encrypted sensitive data
- **Scalable**: Designed for millions of users across India

## API Endpoints Structure

```
/api/v1/
├── input/                        # Core chat functionality
│   ├── POST /chat                # Main chat with RAG enhancement
│   ├── POST /crisis/detect       # Crisis pattern analysis
│   └── POST /family/education    # Family guidance generation
├── voice/                        # Voice processing pipeline
│   ├── POST /transcribe          # Speech-to-text
│   ├── POST /synthesize          # Text-to-speech with cultural tone
│   ├── POST /emotion             # Emotion detection from audio
│   └── POST /pipeline            # Full voice processing pipeline
├── auth/                         # Authentication & user management
│   ├── POST /register            # Anonymous user registration
│   ├── POST /login               # Session management
│   └── GET  /profile             # User preferences and settings
├── peer/                         # Peer support features
│   ├── POST /match               # Cultural peer matching
│   └── GET  /circles             # Active support groups
├── analytics/                    # Usage monitoring (privacy-preserving)
│   ├── GET  /health              # System health and performance
│   └── POST /feedback            # User feedback collection
└── rag/                          # RAG system management
    ├── GET  /status              # RAG system health
    └── POST /search              # Direct knowledge base queries
```

## Coding Conventions & Standards

### Python Backend Standards

- **Type hints**: Mandatory for all function signatures
- **Async patterns**: All service methods use async/await for scalability
- **Error handling**: 3-tier fallback system (RAG → basic → emergency response)
- **Logging**: Structured logging with contextual information
- **Security**: JWT authentication, input validation, rate limiting

### React Frontend Standards

- **TypeScript**: Strict typing for all components and props
- **Component structure**: Functional components with hooks
- **Styling**: Tailwind CSS with responsive design patterns
- **State management**: React hooks for local state, Context for global state

### Cultural & Safety Standards

- **Cultural sensitivity**: Always consider Indian family dynamics and expressions
- **Crisis safety**: Prioritize user safety, escalate to Tele MANAS (14416) when needed
- **Privacy protection**: Anonymous tracking, no PII storage
- **Accessibility**: Voice interaction for users with different literacy levels

## Environment Variables & Configuration

### Required Environment Variables

```bash
# GCP Authentication and Project
GOOGLE_APPLICATION_CREDENTIALS="secrets/secrets.json"
GOOGLE_PROJECT_ID="your-project-id"

# Language and Regional Settings
SUPPORTED_LANGUAGES=["en-US", "hi-IN", "ta-IN", "te-IN"]
DEFAULT_LANGUAGE="en-US"
CULTURAL_REGIONS=["pan_india", "north", "south", "east", "west"]

# Database Configuration
FIRESTORE_DATABASE="mitra-production"

# Security Settings
JWT_SECRET_KEY="your-secret-key"
SESSION_TIMEOUT_MINUTES=60

# Crisis Intervention
TELE_MANAS_PHONE="14416"
TELE_MANAS_ALT_PHONE="1800-891-4416"
```

**Security Note**: Never commit `secrets/secrets.json`, API keys, or JWT secrets to git.

## Database Models & Data Flow

### Core Data Models (`app/models/db_models.py`)

- **AnonymousUser**: Privacy-first user tracking with cultural preferences
- **Conversation**: Chat history with emotion analysis, crisis scores, RAG sources
- **CrisisAlert**: Safety alerts with escalation tracking and intervention logs
- **PeerCircle**: Anonymous peer support groups with cultural matching

### Request/Response Schemas (`app/models/schemas.py`)

- **ChatRequest**/**ChatResponse**: Main conversation API with cultural context
- **VoicePipelineRequest**/**VoicePipelineResponse**: Complete voice processing
- **CrisisDetectionRequest**/**CrisisDetectionResponse**: Risk assessment API
- **FamilyEducationRequest**/**FamilyEducationResponse**: Family guidance generation

## Cultural Intelligence & Mental Health Focus

### This is NOT a generic chatbot - MITRA is specifically designed for:

1. **Indian Youth Mental Health**

   - Understands cultural expressions: "ghabrahat", "mann nahi lagta", "pareshaan"
   - Respects family hierarchy while supporting individual wellbeing
   - Addresses unique pressures: academic competition, arranged marriage, career expectations

2. **Crisis Intervention with Cultural Context**

   - Recognizes Indian cultural expressions of distress
   - Immediate escalation to Tele MANAS (14416) for high-risk scenarios
   - Family-sensitive crisis communication strategies

3. **Multilingual & Culturally-Aware Responses**

   - Language detection and culturally-appropriate response generation
   - Voice interaction with regional accent support
   - Family education respecting traditional values

4. **Privacy-First Mental Health Platform**
   - Anonymous user tracking with Firestore
   - Encrypted sensitive conversations
   - GDPR-compliant data handling

## Testing Strategy & Quality Assurance

### Test Categories

- **Unit Tests**: Individual service testing with mocked dependencies
- **Integration Tests**: Full pipeline testing with real audio and cultural inputs
- **Cultural Tests**: Verify appropriate handling of Hindi expressions and cultural contexts
- **Crisis Safety Tests**: Ensure proper escalation for high-risk scenarios
- **Performance Tests**: Voice processing latency and RAG response times

### Test Data

- **Audio samples**: `tests/audio/` contains multilingual test files
- **Cultural inputs**: Test cases with Hindi expressions and cultural contexts
- **Crisis scenarios**: Graduated risk levels for safety testing

## Deployment & Production Considerations

### Target Infrastructure

- **Backend**: Google Cloud Run (serverless FastAPI)
- **Frontend**: Vercel or Netlify for React deployment
- **Database**: Firestore with multi-region replication
- **Monitoring**: Google Cloud Monitoring + custom analytics

### Scalability Design

- **Concurrent users**: 10,000+ simultaneous conversations
- **Geographic**: Pan-India deployment with regional optimization
- **Languages**: Horizontal scaling for additional Indian languages
- **Cost optimization**: RAG response caching, efficient token usage

## Key Business Logic & Safety Rules

1. **Safety Above All**: Any crisis indicators trigger immediate professional resource recommendations
2. **Cultural Respect**: Honor Indian family values while supporting individual mental health needs
3. **Privacy Protection**: Anonymous conversation tracking, no personal identification storage
4. **Accessibility First**: Voice interaction for users with varying literacy levels
5. **Family Inclusion**: Education and communication tools for generational mental health awareness
6. **Professional Integration**: Seamless handoff to Tele MANAS and local mental health services

## Development Workflow & Contribution Guidelines

### Code Review Standards

- All cultural content reviewed for sensitivity and accuracy
- Crisis detection logic requires safety team approval
- Performance benchmarks for voice processing and RAG response times
- Security review for authentication and data handling changes

### Feature Development Process

1. **Cultural Review**: New features assessed for cultural appropriateness
2. **Safety Testing**: Crisis intervention features tested with mental health professionals
3. **Performance Validation**: Voice and AI response latency within acceptable limits
4. **Privacy Audit**: Data handling compliance with privacy-first principles

**Never give only code give some explanation on what you have done and why have you done**
