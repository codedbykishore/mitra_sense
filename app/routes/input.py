# app/routes/input.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.services.gemini_ai import GeminiService
from app.services.rag_service import RAGService
from typing import Optional, List, Dict, Any
from app.config import Settings

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    context: dict = Field(default_factory=dict)
    language: str = "en"
    region: Optional[str] = None
    max_rag_results: int = 3


class RAGSource(BaseModel):
    text: str
    source: str
    relevance_score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[RAGSource] = []
    context_used: bool = False


gemini_service = GeminiService()
rag_service = RAGService()


def format_rag_context(rag_results: List[Dict[str, Any]]) -> str:
    """Format RAG results into a context string for the LLM."""
    if not rag_results:
        return ""
    
    context_parts = ["Relevant information from our knowledge base:"]
    for i, result in enumerate(rag_results, 1):
        context_parts.append(f"[{i}] {result.get('text', '')}")
    
    return "\n\n".join(context_parts)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        # Get relevant context from RAG
        rag_results = await rag_service.retrieve_with_metadata(
            query=req.text,
            language=req.language,
            region=req.region,
            max_results=req.max_rag_results
        )
        
        # Format the context for the LLM
        rag_context = format_rag_context(rag_results)
        
        # Add RAG context to the existing context
        enhanced_context = {
            **req.context,
            "rag_context": rag_context,
            "sources": [
                {
                    "text": r.get("text", ""),
                    "source": r.get("source_display_name", "Unknown source"),
                    "relevance_score": r.get("relevance_score", 0.0)
                }
                for r in rag_results
            ]
        }
        
        # Get response from Gemini with RAG context
        result = await gemini_service.process_cultural_conversation(
            text=req.text,
            options=enhanced_context,  # Pass context as options
            language=req.language
        )
        
        # Format the response with sources
        # The response from process_cultural_conversation is just the text,
        # so we need to format it with the sources
        response_text = result if isinstance(result, str) else str(result)
        
        return ChatResponse(
            response=response_text,
            sources=[
                RAGSource(
                    text=r.get("text", ""),
                    source=r.get("source_display_name", "Unknown source"),
                    relevance_score=float(r.get("relevance_score", 0.0))
                )
                for r in rag_results
            ],
            context_used=bool(rag_results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )
