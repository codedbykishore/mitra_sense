# app/routes/users.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import OnboardingRequest, OnboardingResponse
from app.services.firestore import FirestoreService
from app.dependencies.auth import get_current_user_from_session


router = APIRouter()
fs = FirestoreService()


@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    current_user: dict = Depends(get_current_user_from_session)
):
    """Complete user onboarding with role and profile information."""
    try:
        user_email = current_user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=401, detail="User not authenticated"
            )

        # Get the user from Firestore
        user = await fs.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if onboarding is already completed
        if user.onboarding_completed:
            raise HTTPException(
                status_code=400,
                detail="Onboarding already completed"
            )

        # Complete onboarding
        await fs.complete_onboarding(
            user.user_id,
            request.role.value,
            request.profile
        )

        return OnboardingResponse(
            success=True,
            message="Onboarding completed successfully",
            user_profile=request.profile
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete onboarding: {str(e)}"
        )


@router.get("/profile")
async def get_user_profile(
    current_user: dict = Depends(get_current_user_from_session)
):
    """Get current user's profile and onboarding status."""
    try:
        user_email = current_user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=401, detail="User not authenticated"
            )

        user = await fs.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "onboarding_completed": user.onboarding_completed,
            "role": user.role,
            "profile": user.profile,
            "email": user.email,
            "user_id": user.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user profile: {str(e)}"
        )
