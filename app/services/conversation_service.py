# app/services/conversation_service.py
from typing import List, Dict
from app.services.firestore import FirestoreService
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation and message management operations."""

    def __init__(self):
        self.firestore_service = FirestoreService()

    async def get_recent_context(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch recent messages for RAG context.

        Queries Firestore for messages in the given conversation, orders them
        descending by timestamp, limits to the last N messages, and returns
        them in ascending order (oldest → newest) for proper conversation flow.

        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of recent messages to return (default: 10)

        Returns:
            List of message dictionaries ordered chronologically
            (oldest → newest). Empty list if conversation not found or no messages
        """
        try:
            logger.info(
                f"Fetching recent context for conversation {conversation_id} "
                f"with limit {limit}"
            )
            
            # Verify conversation exists
            conversation = await self.firestore_service.get_conversation(
                conversation_id
            )
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return []
            
            # Query messages ordered by timestamp descending, limit to recent N
            messages_ref = (
                self.firestore_service.db.collection("conversations")
                .document(conversation_id)
                .collection("messages")
            )
            
            # Get most recent N messages (timestamp descending)
            query = messages_ref.order_by(
                "timestamp", direction="DESCENDING"
            ).limit(limit)
            
            recent_messages = []
            async for doc in query.stream():
                message_data = doc.to_dict()
                recent_messages.append(message_data)
            
            # Reverse to get chronological order (oldest → newest)
            context_messages = list(reversed(recent_messages))
            
            logger.info(
                f"Retrieved {len(context_messages)} messages for RAG context "
                f"from conversation {conversation_id}"
            )
            
            return context_messages
            
        except Exception as e:
            logger.error(
                f"Error fetching recent context for conversation "
                f"{conversation_id}: {e}"
            )
            return []
    
    async def format_context_for_rag(
        self,
        messages: List[Dict],
        include_metadata: bool = True
    ) -> str:
        """
        Format conversation messages for RAG prompt context.
        
        Args:
            messages: List of message dictionaries from get_recent_context
            include_metadata: Whether to include timestamp and mood data
            
        Returns:
            Formatted string ready for AI prompt inclusion
        """
        if not messages:
            return ""
        
        formatted_context = "Recent conversation context:\n"
        
        for msg in messages:
            sender = "User" if msg.get("sender_id") != "ai" else "AI Assistant"
            text = msg.get("text", "")
            
            # Basic message format
            formatted_context += f"{sender}: {text}\n"
            
            # Include metadata if requested
            if include_metadata:
                timestamp = msg.get("timestamp")
                mood_score = msg.get("mood_score")
                
                if timestamp:
                    formatted_context += f"  [Time: {timestamp}]\n"
                if mood_score:
                    formatted_context += f"  [Mood: {mood_score}]\n"
        
        formatted_context += "\n"
        return formatted_context
    
    async def get_conversation_summary(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> Dict[str, any]:
        """
        Get conversation summary including recent context and metadata.
        
        Args:
            conversation_id: The ID of the conversation
            limit: Number of recent messages to include
            
        Returns:
            Dictionary containing conversation metadata and recent messages
        """
        try:
            # Get conversation metadata
            conversation = await self.firestore_service.get_conversation(
                conversation_id
            )
            if not conversation:
                return {}
            
            # Get recent messages for context
            recent_messages = await self.get_recent_context(
                conversation_id, limit
            )
            
            # Format context string for easy AI consumption
            formatted_context = await self.format_context_for_rag(
                recent_messages
            )
            
            return {
                "conversation_id": conversation_id,
                "participants": conversation.participants,
                "created_at": conversation.created_at,
                "last_active_at": conversation.last_active_at,
                "recent_messages": recent_messages,
                "formatted_context": formatted_context,
                "message_count": len(recent_messages)
            }
            
        except Exception as e:
            logger.error(
                f"Error getting conversation summary for "
                f"{conversation_id}: {e}"
            )
            return {}
    
    async def validate_user_access(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        Validate that a user has access to a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            user_id: The ID of the user requesting access
            
        Returns:
            True if user is a participant, False otherwise
        """
        try:
            conversation = await self.firestore_service.get_conversation(
                conversation_id
            )
            if not conversation:
                return False
            
            return user_id in conversation.participants
            
        except Exception as e:
            logger.error(
                f"Error validating user access for conversation "
                f"{conversation_id}, user {user_id}: {e}"
            )
            return False
