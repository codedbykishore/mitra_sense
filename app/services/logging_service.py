"""Logging Service for tracking access to sensitive data."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.services.firestore import FirestoreService
from app.models.db_models import AccessLog

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logging access to sensitive user data."""
    
    def __init__(self, firestore_service: FirestoreService):
        self.firestore = firestore_service
    
    async def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        performed_by: str,
        performed_by_role: str = "unknown",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Log access to user data.
        
        Args:
            user_id: ID of the user whose data was accessed
            resource: Type of resource ("moods", "conversations", etc.)
            action: Action performed ("view", "export", "list", etc.)
            performed_by: ID of the user who performed the action
            performed_by_role: Role of the person performing the action
            metadata: Additional context information
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            log_id = str(uuid.uuid4())
            access_log = AccessLog(
                log_id=log_id,
                user_id=user_id,
                resource=resource,
                action=action,
                performed_by=performed_by,
                performed_by_role=performed_by_role,
                timestamp=datetime.now(timezone.utc),
                metadata=metadata or {}
            )
            
            # Store the access log in Firestore
            await self.firestore.db.collection("access_logs").document(
                log_id
            ).set(access_log.model_dump())
            
            logger.info(
                f"Logged access: user={user_id}, resource={resource}, "
                f"action={action}, by={performed_by}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to log access: {e}")
            return False
    
    async def get_access_logs(
        self, user_id: str, limit: int = 50
    ) -> List[AccessLog]:
        """
        Get access logs for a specific user.
        
        Args:
            user_id: ID of the user whose access logs to retrieve
            limit: Maximum number of logs to return
            
        Returns:
            List of AccessLog objects
        """
        try:
            logs_ref = self.firestore.db.collection("access_logs")
            query = (
                logs_ref.where("user_id", "==", user_id)
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            
            logs = []
            async for doc in query.stream():
                try:
                    log_data = doc.to_dict()
                    logs.append(AccessLog(**log_data))
                except Exception as e:
                    logger.error(f"Error parsing access log {doc.id}: {e}")
                    continue
            
            logger.info(
                f"Retrieved {len(logs)} access logs for user {user_id}"
            )
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving access logs: {e}")
            return []
    
    async def get_recent_access_logs(
        self, limit: int = 100
    ) -> List[AccessLog]:
        """
        Get recent access logs across all users (admin view).
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of AccessLog objects
        """
        try:
            logs_ref = self.firestore.db.collection("access_logs")
            query = (
                logs_ref.order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            
            logs = []
            async for doc in query.stream():
                try:
                    log_data = doc.to_dict()
                    logs.append(AccessLog(**log_data))
                except Exception as e:
                    logger.error(f"Error parsing access log {doc.id}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(logs)} recent access logs")
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving recent access logs: {e}")
            return []
