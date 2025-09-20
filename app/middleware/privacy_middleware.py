"""Privacy middleware for Feature 5 - Privacy Flags and Access Logging."""

import logging
from typing import Dict, Callable
from fastapi import HTTPException, status
from app.services.privacy_service import PrivacyService
from app.services.logging_service import LoggingService

logger = logging.getLogger(__name__)


class PrivacyMiddleware:
    """Middleware for checking privacy flags and logging access."""
    
    def __init__(
        self,
        privacy_service: PrivacyService,
        logging_service: LoggingService
    ):
        self.privacy_service = privacy_service
        self.logging_service = logging_service
    
    async def check_and_log_access(
        self,
        target_user_id: str,
        resource_type: str,
        action: str,
        current_user: Dict,
        metadata: Dict[str, str] = None
    ) -> bool:
        """
        Check privacy flags and log access attempt.
        
        Args:
            target_user_id: ID of user whose data is being accessed
            resource_type: Type of resource ("moods", "conversations")
            action: Action being performed ("view", "export", "list")
            current_user: Current user session data
            metadata: Additional context
            
        Returns:
            bool: True if access allowed, raises HTTPException if denied
            
        Raises:
            HTTPException: If access is denied due to privacy settings
        """
        try:
            # Check if the user is accessing their own data
            if current_user["user_id"] == target_user_id:
                # Users can always access their own data
                await self.logging_service.log_access(
                    user_id=target_user_id,
                    resource=resource_type,
                    action=action,
                    performed_by=current_user["user_id"],
                    performed_by_role=current_user.get("role", "student"),
                    metadata=metadata or {}
                )
                return True
            
            # Check privacy flags for external access
            privacy_check = await self.privacy_service.check_flags(
                target_user_id, resource_type
            )
            
            if not privacy_check["exists"]:
                # Log the failed attempt
                await self.logging_service.log_access(
                    user_id=target_user_id,
                    resource=resource_type,
                    action=f"{action}_failed",
                    performed_by=current_user["user_id"],
                    performed_by_role=current_user.get("role", "unknown"),
                    metadata={
                        **(metadata or {}),
                        "reason": "user_not_found"
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if not privacy_check["allowed"]:
                # Log the denied access attempt
                await self.logging_service.log_access(
                    user_id=target_user_id,
                    resource=resource_type,
                    action=f"{action}_denied",
                    performed_by=current_user["user_id"],
                    performed_by_role=current_user.get("role", "unknown"),
                    metadata={
                        **(metadata or {}),
                        "reason": "privacy_flag_disabled"
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access to {resource_type} is restricted by "
                           f"user privacy settings"
                )
            
            # Access allowed - log the successful access
            await self.logging_service.log_access(
                user_id=target_user_id,
                resource=resource_type,
                action=action,
                performed_by=current_user["user_id"],
                performed_by_role=current_user.get("role", "unknown"),
                metadata=metadata or {}
            )
            
            return True
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in privacy middleware: {e}")
            # Log the error attempt
            await self.logging_service.log_access(
                user_id=target_user_id,
                resource=resource_type,
                action=f"{action}_error",
                performed_by=current_user["user_id"],
                performed_by_role=current_user.get("role", "unknown"),
                metadata={
                    **(metadata or {}),
                    "error": str(e)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking privacy settings"
            )


def create_privacy_decorator(
    privacy_service: PrivacyService,
    logging_service: LoggingService,
    resource_type: str,
    action: str
) -> Callable:
    """
    Create a decorator for privacy checking and access logging.
    
    Args:
        privacy_service: Privacy service instance
        logging_service: Logging service instance
        resource_type: Type of resource being accessed
        action: Action being performed
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Extract target_user_id and current_user from function parameters
            target_user_id = kwargs.get('student_id') or kwargs.get('user_id')
            current_user = kwargs.get('current_user')
            
            if not target_user_id or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing required parameters for privacy check"
                )
            
            # Create middleware instance and check privacy
            middleware = PrivacyMiddleware(privacy_service, logging_service)
            await middleware.check_and_log_access(
                target_user_id=target_user_id,
                resource_type=resource_type,
                action=action,
                current_user=current_user
            )
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
