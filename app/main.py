import logging
# Main application setup with middleware and routing
from fastapi import FastAPI, middleware
# from fastapi.middleware.cors import CORSMiddleware
# from app.routes import crisis, family, peer, input, analytics
# from app.services.security import SecurityMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MITRA - Mental Intelligence Through Responsive AI",
    description="Culturally-aware mental wellness AI for Indian youth",
    version="1.0.0",
)

# Security & Privacy Middleware
# app.add_middleware(SecurityMiddleware)
# app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Route Registration
# app.include_router(input.router, prefix="/api/v1/input")
# app.include_router(crisis.router, prefix="/api/v1/crisis")
# app.include_router(peer.router, prefix="/api/v1/peer")
# app.include_router(family.router, prefix="/api/v1/family")
# app.include_router(analytics.router, prefix="/api/v1/analytics")


from app.routes.input import router as input_router
from app.routes.voice import router as voice_router

app.include_router(input_router, prefix="/api/v1/input")
app.include_router(voice_router, prefix="/api/v1")


@app.get("/")
def root():
    logger.info("Root endpoint accessed.")
    return {"message": "root end point"}
