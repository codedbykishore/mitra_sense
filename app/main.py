import logging
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import os
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MITRA - Mental Intelligence Through Responsive AI",
    description="Culturally-aware mental wellness AI for Indian youth",
    version="1.0.0",
)

# ✅ Add CORS Middleware
origins = [
    "http://localhost:5173",  # React dev server (Vite)
    "http://127.0.0.1:5173",  # Sometimes React runs on 127.0.0.1
]

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] to allow all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # allow all headers
)

# Route Registration
from app.routes.input import router as input_router
from app.routes.voice import router as voice_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.conversations import router as conversations_router
from app.routes.students import router as students_router
from app.routes.mood import router as mood_router
from app.routes.crisis import router as crisis_router
from app.routes.privacy import router as privacy_router
from app.services.gemini_ai import GeminiService

app.include_router(crisis_router, prefix="/api/v1/crisis", tags=["crisis"])
app.include_router(input_router, prefix="/api/v1/input")
app.include_router(voice_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(students_router, prefix="/api/v1", tags=["students"])
app.include_router(mood_router, prefix="/api/v1", tags=["mood"])
app.include_router(
    conversations_router, prefix="/api/v1", tags=["conversations"]
)
app.include_router(privacy_router, tags=["privacy"])
app.include_router(auth_router, prefix="")

rag_corpus_name = getattr(settings, "CORPUS_NAME", None)
gemini_service = GeminiService(rag_corpus_name=rag_corpus_name)


@app.get("/")
def root():
    logger.info("Root endpoint accessed.")
    return {"message": "root end point"}


@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "mitra-backend"}


@app.middleware("http")
async def block_well_known(request: Request, call_next):
    if request.url.path.startswith("/.well-known"):
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)
