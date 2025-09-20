# app/routes/input.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from app.services.gemini_ai import GeminiService
from app.services.rag_service import RAGService
from app.services.firestore import FirestoreService
from app.services.conversation_service import ConversationService
from app.services.emotion_analysis import EmotionAnalysisService
from typing import Optional, List, Dict, Any
from app.config import Settings
import uuid
from datetime import datetime, timezone
import json
from langdetect import detect, LangDetectException, DetectorFactory

# Ensure consistent language detection results
DetectorFactory.seed = 0

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    context: dict = Field(default_factory=dict)
    language: str = "en"
    region: Optional[str] = None
    max_rag_results: int = 3
    force_new_conversation: bool = False
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to fetch recent context from"
    )
    include_conversation_context: bool = Field(
        True,
        description="Whether to include recent conversation history for RAG"
    )
    context_limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of recent messages to include as context"
    )


class RAGSource(BaseModel):
    text: str
    source: str
    relevance_score: float


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[RAGSource] = []
    context_used: bool = False


gemini_service = GeminiService()
rag_service = RAGService()
firestore_service = FirestoreService()
conversation_service = ConversationService()
emotion_analysis_service = EmotionAnalysisService()


def format_rag_context(rag_results: List[Dict[str, Any]]) -> str:
    """Format RAG results into a context string for the LLM."""
    if not rag_results:
        return ""

    context_parts = ["Relevant information from our knowledge base:"]
    for i, result in enumerate(rag_results, 1):
        context_parts.append(f"[{i}] {result.get('text', '')}")

    return "\n\n".join(context_parts)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    request: Request
):
    try:
        # Get current user from session (optional for backwards compatibility)
        current_user = None
        user_id = "anonymous"
        
        if hasattr(request, 'session') and request.session:
            current_user = request.session.get("user")
            if current_user and isinstance(current_user, dict):
                user_id = (
                    current_user.get("user_id") or
                    current_user.get("email", "anonymous")
                )
            elif current_user:
                # Handle case where user might be a string or other format
                user_id = str(current_user)
        
        # Use provided conversation_id or create/get one for the user
        if req.conversation_id:
            conversation_id = req.conversation_id
            # Validate user has access to this conversation
            if user_id != "anonymous":
                has_access = await conversation_service.validate_user_access(
                    conversation_id, user_id
                )
                if not has_access:
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied to conversation"
                    )
        else:
            conversation_id = await (
                firestore_service.create_or_update_conversation(
                    user_id, force_new=req.force_new_conversation
                )
            )

        # Fetch recent conversation context if requested
        conversation_context = ""
        if req.include_conversation_context:
            try:
                recent_messages = await (
                    conversation_service.get_recent_context(
                        conversation_id, limit=req.context_limit
                    )
                )
                if recent_messages:
                    conversation_context = (
                        await conversation_service.format_context_for_rag(
                            recent_messages, include_metadata=False
                        )
                    )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Could not fetch conversation context: {e}")

        # Detect language from user input
        detected_language = req.language
        try:
            detected_language = detect(req.text)
        except LangDetectException:
            detected_language = "en"

        # Save user message to Firestore
        user_message_id = str(uuid.uuid4())
        user_message_data = {
            "message_id": user_message_id,
            "conversation_id": conversation_id,
            "sender_id": user_id,
            "text": req.text,
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "user",
                "language": detected_language,
                "embedding_id": None,
                "emotion_score": "{}"
            }
        }
        await firestore_service.save_message(
            conversation_id, user_message_data
        )

        # Perform automatic mood inference from the user's message
        mood_inference = None
        if user_id != "anonymous":  # Only for authenticated users
            try:
                mood_inference = await emotion_analysis_service.process_message_for_mood_inference(
                    user_id=user_id,
                    message_text=req.text,
                    language=detected_language,
                    conversation_id=conversation_id
                )
                
                # Update emotion_score in the saved message if inference was successful
                if mood_inference:
                    user_message_data["metadata"]["emotion_score"] = json.dumps(mood_inference.get("emotions", {}))
                    await firestore_service.save_message(conversation_id, user_message_data)
                    
            except Exception as e:
                # Don't fail the chat if mood inference fails
                print(f"Mood inference failed for user {user_id}: {e}")

        # Get relevant context from RAG
        rag_results = await rag_service.retrieve_with_metadata(
            query=req.text,
            language=req.language,
            region=req.region,
            max_results=req.max_rag_results,
        )

        # Format the context for the LLM
        rag_context = format_rag_context(rag_results)

        # Add RAG context and conversation context to the existing context
        enhanced_context = {
            **req.context,
            "rag_context": rag_context,
            "conversation_context": conversation_context,
            "sources": [
                {
                    "text": r.get("text", ""),
                    "source": r.get("source_display_name", "Unknown source"),
                    "relevance_score": r.get("relevance_score", 0.0),
                }
                for r in rag_results
            ],
        }

        # Get response from Gemini with RAG context
        result = await gemini_service.process_cultural_conversation(
            text=req.text,
            options=enhanced_context,  # Pass context as options
            language=req.language,
        )

        # Format the response with sources
        response_text = result if isinstance(result, str) else str(result)

        # Save AI response to Firestore
        ai_message_id = str(uuid.uuid4())
        ai_message_data = {
            "message_id": ai_message_id,
            "conversation_id": conversation_id,
            "sender_id": "ai",
            "text": response_text,
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "ai",
                "language": detected_language,
                "embedding_id": None,
                "emotion_score": "{}"
            }
        }
        await firestore_service.save_message(
            conversation_id, ai_message_data
        )

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=[
                RAGSource(
                    text=r.get("text", ""),
                    source=r.get("source_display_name", "Unknown source"),
                    relevance_score=float(r.get("relevance_score", 0.0)),
                )
                for r in rag_results
            ],
            context_used=bool(rag_results),
            mood_inference=mood_inference
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing your request: {str(e)}"
        )
