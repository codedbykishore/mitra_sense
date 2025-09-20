# app/routes/users.py
import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    OnboardingRequest, OnboardingResponse,
    InstitutionsListResponse, InstitutionInfo
)
from app.models.db_models import Institution
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

        # Handle institution role
        if request.role.value == "institution":
            institution_name = request.profile.get("institution_name")
            if not institution_name:
                raise HTTPException(
                    status_code=400,
                    detail="Institution name is required"
                )

            # Check if institution name already exists (case-insensitive)
            existing_institution = await fs.get_institution_by_name(
                institution_name.strip()
            )
            if existing_institution:
                raise HTTPException(
                    status_code=400,
                    detail="Institution name already exists"
                )

            # Create new institution
            institution_id = str(uuid.uuid4())
            institution = Institution(
                institution_id=institution_id,
                institution_name=institution_name.strip(),
                contact_person=request.profile.get("contact_person", ""),
                region=request.profile.get("region", ""),
                email=user_email,
                user_id=user.user_id
            )
            await fs.create_institution(institution)

        # Handle student role
        elif request.role.value == "student":
            # Validate institution_id if provided
            if request.institution_id:
                institution = await fs.get_institution(request.institution_id)
                if not institution:
                    raise HTTPException(
                        status_code=400,
                        detail="Selected institution not found"
                    )
                # Increment student count
                await fs.increment_student_count(request.institution_id)

        # Complete onboarding
        await fs.complete_onboarding(
            user.user_id,
            request.role.value,
            request.profile,
            request.institution_id
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


@router.get("/institutions", response_model=InstitutionsListResponse)
async def get_institutions():
    """Get list of all active institutions for student onboarding."""
    try:
        institutions = await fs.list_institutions()
        
        # Convert to response format
        institution_list = [
            InstitutionInfo(
                institution_id=inst.institution_id,
                institution_name=inst.institution_name,
                region=inst.region,
                student_count=inst.student_count,
                active=inst.active
            ) for inst in institutions
        ]

        return InstitutionsListResponse(institutions=institution_list)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get institutions: {str(e)}"
        )



