# Main application setup with middleware and routing
from fastapi import FastAPI, middleware
# from fastapi.middleware.cors import CORSMiddleware
# from app.routes import crisis, family, peer, input, analytics
# from app.services.security import SecurityMiddleware

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


@app.get("/")
def root():
    return {"message": "root end point"}
