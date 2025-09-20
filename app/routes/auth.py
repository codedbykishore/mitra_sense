# app/routes/auth.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from app.models.db_models import User
from app.services.firestore import FirestoreService
from app.config import settings

router = APIRouter()
fs = FirestoreService()

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


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/me")
async def get_current_user(request: Request):
    user = request.session.get("user")

    if not user:
        return JSONResponse(
            {"authenticated": False, "user": None},
            status_code=401
        )

    # Get full user info from Firestore for onboarding status
    email = user.get("email")
    if email:
        firestore_user = await fs.get_user_by_email(email)
        onboarding_completed = (
            firestore_user.onboarding_completed if firestore_user else False
        )
        role = firestore_user.role if firestore_user else None
        profile = firestore_user.profile if firestore_user else {}
    else:
        onboarding_completed = False
        role = None
        profile = {}

    return {
        "authenticated": True,
        "name": user.get("name"),
        "email": user.get("email"),
        "picture": user.get("picture"),
        "plan": user.get("plan", "Free"),
        "onboarding_completed": onboarding_completed,
        "role": role,
        "profile": profile
    }


@router.get("/auth/google/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    email = user_info["email"]
    google_id = user_info.get("sub")
    name = user_info.get("name")
    picture = user_info.get("picture")

    # Check Firestore
    existing = await fs.get_user_by_email(email)
    if not existing:
        user = User(
            user_id=email,
            email=email,
            google_id=google_id,
            name=name,
            picture=picture
        )
        await fs.create_user(user)
        # New user needs onboarding
        request.session["user"] = dict(user_info)
        return RedirectResponse(url="http://localhost:3000/onboarding")
    else:
        # Existing user - check onboarding status
        request.session["user"] = dict(user_info)
        if not existing.onboarding_completed:
            return RedirectResponse(url="http://localhost:3000/onboarding")
        else:
            return RedirectResponse(url="http://localhost:3000/")


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"message": "Logged out"})
