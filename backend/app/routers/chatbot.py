from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'model'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User prompt")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation turns")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Optional client context")

class ChatResponse(BaseModel):
    reply: str
    provider: str
    timestamp: str

@router.post("/message", response_model=ChatResponse)
def send_chat_message(request: ChatRequest):
    """
    Public AI Chatbot endpoint for answering platform, assessment, proctoring,
    and technical questions. Employs direct Gemini API with an automatic,
    comprehensive fallback knowledge engine.
    """
    history_dicts = [m.model_dump() for m in request.history] if request.history else []
    result = ChatbotService.get_response(
        message=request.message,
        history=history_dicts,
        context=request.context
    )
    return result

@router.get("/status")
def get_chatbot_status():
    """
    Check AI Chatbot service health and whether Gemini API key is configured.
    """
    has_gemini = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    return {
        "status": "online",
        "gemini_configured": has_gemini,
        "active_model": settings.GEMINI_MODEL if has_gemini else "SkillSphere Built-in Knowledge Engine",
        "mode": "Gemini 1.5/2.0 API" if has_gemini else "SkillSphere Native AI Engine",
        "timestamp": datetime.utcnow().isoformat()
    }
