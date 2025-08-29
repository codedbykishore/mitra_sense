import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ uncomment this

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # allow all headers
)

# Route Registration
from app.routes.input import router as input_router
from app.routes.voice import router as voice_router

app.include_router(input_router, prefix="/api/v1/input")
app.include_router(voice_router, prefix="/api/v1")


@app.get("/")
def root():
    logger.info("Root endpoint accessed.")
    return {"message": "root end point"}
