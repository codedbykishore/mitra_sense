"""Privacy Service for managing user privacy flags and access control."""

import logging
from typing import Optional, Dict
from app.services.firestore import FirestoreService

logger = logging.getLogger(__name__)


class PrivacyService:
    """Service for managing privacy flags and access control."""
    
    def __init__(self, firestore_service: FirestoreService):
        self.firestore = firestore_service
    
    async def check_flags(
        self, user_id: str, resource_type: str
    ) -> Dict[str, bool]:
        """
        Check privacy flags for a user and resource type.
        
        Args:
            user_id: The ID of the user whose data is being accessed
            resource_type: Type of resource ("moods" or "conversations")
            
        Returns:
            Dict with "allowed" and "exists" keys
        """
        try:
            user = await self.firestore.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for privacy check")
                return {"allowed": False, "exists": False}
            
            privacy_flags = user.privacy_flags
            
            if resource_type == "moods":
                allowed = privacy_flags.get("share_moods", True)
            elif resource_type == "conversations":
                allowed = privacy_flags.get("share_conversations", True)
            else:
                logger.warning(f"Unknown resource type: {resource_type}")
                allowed = False
            
            status = 'allowed' if allowed else 'denied'
            logger.info(
                f"Privacy check for user {user_id}, "
                f"resource {resource_type}: {status}"
            )
            
            return {"allowed": allowed, "exists": True}
            
        except Exception as e:
            logger.error(f"Error checking privacy flags: {e}")
            return {"allowed": False, "exists": False}
    
    async def update_privacy_flags(
        self, user_id: str, privacy_flags: Dict[str, bool]
    ) -> bool:
        """
        Update privacy flags for a user.
        
        Args:
            user_id: The ID of the user
            privacy_flags: Dictionary of privacy flags to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate the privacy flags
            valid_flags = {"share_moods", "share_conversations"}
            if not all(flag in valid_flags for flag in privacy_flags.keys()):
                logger.error(f"Invalid privacy flags: {privacy_flags}")
                return False
            
            await self.firestore.update_user(user_id, {
                "privacy_flags": privacy_flags
            })
            
            logger.info(f"Updated privacy flags for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating privacy flags: {e}")
            return False
    
    async def get_privacy_flags(
        self, user_id: str
    ) -> Optional[Dict[str, bool]]:
        """
        Get privacy flags for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary of privacy flags or None if user not found
        """
        try:
            user = await self.firestore.get_user(user_id)
            if not user:
                return None
            
            return user.privacy_flags
            
        except Exception as e:
            logger.error(f"Error getting privacy flags: {e}")
            return None
