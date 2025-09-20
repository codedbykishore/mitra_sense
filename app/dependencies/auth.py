# app/dependencies/auth.py
from fastapi import HTTPException, status, Request
from app.models.db_models import User
from app.services.firestore import FirestoreService


async def get_current_user_from_session(request: Request) -> User:
    """Get current user from session (used with Google OAuth)."""
    if not hasattr(request, 'session'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not available"
        )
    
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    # Get the user's email from session
    email = user_session.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User email not found in session"
        )
    
    # Fetch the full User object from Firestore
    fs = FirestoreService()
    user = await fs.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database"
        )
    
    return user
