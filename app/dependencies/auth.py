# app/dependencies/auth.py
from fastapi import HTTPException, status, Request


async def get_current_user_from_session(request: Request) -> dict:
    """Get current user from session (used with Google OAuth)."""
    if not hasattr(request, 'session'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not available"
        )
    
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    return user
