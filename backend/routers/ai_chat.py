"""AI Chat proxy endpoint — routes LLM requests to the configured provider.

All LLM API keys live exclusively on the backend.
The browser must never contact LLM providers directly.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.schemas.response import ErrorResponse
from backend.security.limits import AI_CHAT_LIMIT
from backend.dependencies.auth import get_current_user
from backend.security.rate_limit import limiter
from backend.services.llm_service import (
    LLMConfigError,
    LLMError,
    LLMRateLimitError,
    chat as llm_chat,
)

logger = logging.getLogger("backend.ai_chat")
router = APIRouter(prefix="/api/ai", tags=["AI Chat"])


class ChatRequest(BaseModel):
    provider: str = Field(..., description="LLM provider: gemini, openai, anthropic, groq")
    model: str | None = Field(default=None, description="Model name override")
    messages: list[dict[str, str]] = Field(..., min_length=1, description="Chat messages with role and content")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: int = Field(default=1024, ge=1, le=65536, description="Maximum output tokens")


class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: dict | None = None


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid provider or request"},
        401: {"model": ErrorResponse, "description": "Missing backend API key"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Provider internal error"},
    },
    summary="Chat dengan LLM melalui backend proxy",
    description="Mengirim pesan ke LLM provider melalui backend. "
                "API key provider hanya disimpan di backend.",
)
@limiter.limit(AI_CHAT_LIMIT)
async def chat(request: Request, req: ChatRequest, _: object = Depends(get_current_user)) -> ChatResponse:
    try:
        result = await llm_chat(
            provider=req.provider,
            model=req.model,
            messages=req.messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        return ChatResponse(**result)
    except LLMConfigError as exc:
        if "Unsupported provider" in str(exc) or "No messages" in str(exc):
            raise HTTPException(status_code=400, detail=str(exc))
        raise HTTPException(status_code=401, detail=str(exc))
    except LLMRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except LLMError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
