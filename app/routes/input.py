# app/routes/input.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini_ai import GeminiService

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    context: dict = {}


class ChatResponse(BaseModel):
    response: str


gemini_service = GeminiService()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        result = await gemini_service.process_cultural_conversation(
            req.text, req.context
        )
        return ChatResponse(response=result.get("response", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini AI error: {e}")
