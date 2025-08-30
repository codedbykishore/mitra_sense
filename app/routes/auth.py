# app/routes/auth.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from passlib.context import CryptContext
from app.models.db_models import User
from app.services.firestore import FirestoreService
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.config import settings  # Import project settings

router = APIRouter()
fs = FirestoreService()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(request: SignupRequest):
    # Check if user exists
    existing = await fs.get_user_by_email(request.email)  # <-- await here
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(request.password)

    user = User(
        user_id=request.email,  # or generate UUID
        email=request.email,
        hashed_password=hashed,
    )

    await fs.create_user(user)  # <-- also await this
    return {"message": "User created successfully"}


@router.post("/login")
async def login(request: LoginRequest):
    # Get the user by email
    user = await fs.get_user_by_email(request.email)
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user.user_id}


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    email = user_info["email"]

    # Check Firestore
    existing = await fs.get_user_by_email(email)
    if not existing:
        user = User(
            user_id=email,
            email=email,
            hashed_password="",  # empty since Google handles auth
        )
        await fs.create_user(user)

    request.session["user"] = dict(user_info)
    return JSONResponse({"message": "Login successful", "user": user_info})


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"message": "Logged out"})
