# app/routes/conversations.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.firestore import FirestoreService
from app.dependencies.auth import get_current_user_from_session
from app.models.db_models import User
from app.models.schemas import (
    ConversationsListResponse, ConversationMessagesResponse,
    ConversationInfo, MessageInfo
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/conversations")
async def get_user_conversations(
    current_user: User = Depends(get_current_user_from_session)
) -> ConversationsListResponse:
    """
    Get all conversations for the current user.
    
    Returns:
        List of conversations with metadata, sorted by last activity
    """
    try:
        firestore_service = FirestoreService()
        conversations = await firestore_service.get_user_conversations(
            current_user.user_id
        )
        
        # Transform conversations to include only necessary metadata
        conversation_list = []
        for conv in conversations:
            created_at = conv.get("created_at")
            last_active_at = conv.get("last_active_at")
            
            conversation_info = ConversationInfo(
                conversation_id=conv["conversation_id"],
                participants=conv.get("participants", []),
                created_at=str(created_at) if created_at else None,
                last_active_at=str(last_active_at) if last_active_at else None,
                participant_count=len(conv.get("participants", []))
            )
            conversation_list.append(conversation_info)
        
        return ConversationsListResponse(
            conversations=conversation_list,
            total_count=len(conversation_list)
        )
        
    except Exception as e:
        logger.error(
            f"Error fetching conversations for user "
            f"{current_user.user_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversations"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user_from_session)
) -> ConversationMessagesResponse:
    """
    Get messages for a specific conversation.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (1-100)
        
    Returns:
        Messages ordered by timestamp (oldest first) with pagination info
    """
    try:
        firestore_service = FirestoreService()
        
        # First, verify the user has access to this conversation
        conversation = await firestore_service.get_conversation(
            conversation_id
        )
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        # Check if current user is a participant
        if current_user.user_id not in conversation.participants:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Not a participant in this conversation"
            )
        
        # Get messages
        messages_data = await firestore_service.get_messages(
            conversation_id, limit
        )
        
        # Transform messages to use proper schema
        messages = []
        for msg_data in messages_data:
            message_info = MessageInfo(
                message_id=msg_data["message_id"],
                conversation_id=msg_data["conversation_id"],
                sender_id=msg_data["sender_id"],
                text=msg_data["text"],
                timestamp=str(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {}),
                mood_score=msg_data.get("mood_score")
            )
            messages.append(message_info)
        
        return ConversationMessagesResponse(
            conversation_id=conversation_id,
            messages=messages,
            message_count=len(messages),
            limit=limit,
            has_more=len(messages) == limit
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            f"Error fetching messages for conversation "
            f"{conversation_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve messages"
        )
