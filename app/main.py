from fastapi import FastAPI
from app.routes import input, crisis, peer, family, analytics

app = FastAPI(title="Mental Health MVP", version="0.1")

# Register routers
app.include_router(input.router, prefix="/api", tags=["Input"])
app.include_router(crisis.router, prefix="/api", tags=["Crisis"])
app.include_router(peer.router, prefix="/api", tags=["Peer"])
app.include_router(family.router, prefix="/api", tags=["Family"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.get("/ping")
def ping():
    return {"msg": "pong"}
