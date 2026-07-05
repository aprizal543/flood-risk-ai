"""LLM provider abstraction — all provider-specific logic lives here.

The router must never contain provider logic.
API keys are read from backend environment variables only.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger("backend.llm")

ENV_KEY_MAP: dict[str, str] = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
}

DEFAULT_MODELS: dict[str, str] = {
    "gemini": "gemini-2.0-flash",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "groq": "llama-3.1-8b-instant",
}


class LLMError(RuntimeError):
    """Raised when an LLM provider request fails."""


class LLMConfigError(LLMError):
    """Raised when provider configuration is missing or invalid."""


class LLMRateLimitError(LLMError):
    """Raised when the provider returns a rate-limit response."""



def _get_api_key(provider: str) -> str:
    env_var = ENV_KEY_MAP.get(provider)
    if not env_var:
        raise LLMConfigError(f"Unsupported provider: {provider}")
    key = os.getenv(env_var)
    if not key:
        raise LLMConfigError(f"Missing {env_var} for provider {provider}")
    return key


def _common_messages(messages: list[dict[str, str]]) -> str | None:
    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    return "\n\n".join(system_parts) if system_parts else None


def _non_system_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [m for m in messages if m.get("role") != "system"]


async def _call_gemini(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    system = _common_messages(messages)
    contents = []
    for m in _non_system_messages(messages):
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    body: dict[str, Any] = {"contents": contents}
    if system:
        body["system_instruction"] = {"parts": [{"text": system}]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=body)

    if resp.status_code == 429:
        raise LLMRateLimitError("Gemini rate limit exceeded")
    if resp.status_code >= 400:
        raise LLMError(f"Gemini API error: {resp.status_code} {resp.text[:200]}")

    data = resp.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    usage = data.get("usageMetadata", {})
    return {
        "content": text or "Maaf, saya tidak dapat menjawab saat ini.",
        "usage": {
            "prompt_tokens": usage.get("promptTokenCount"),
            "completion_tokens": usage.get("candidatesTokenCount"),
            "total_tokens": usage.get("totalTokenCount"),
        },
    }


async def _call_openai_compat(
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            base_url,
            json=body,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    if resp.status_code == 429:
        raise LLMRateLimitError(f"Rate limit exceeded for {base_url}")
    if resp.status_code >= 400:
        raise LLMError(f"OpenAI-compatible API error: {resp.status_code} {resp.text[:200]}")

    data = resp.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content")
    usage = data.get("usage", {})
    return {
        "content": text or "Maaf, saya tidak dapat menjawab saat ini.",
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
    }


async def _call_anthropic(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    system = _common_messages(messages)
    msgs = _non_system_messages(messages)

    body: dict[str, Any] = {
        "model": model,
        "messages": msgs,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if system:
        body["system"] = system

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            json=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )

    if resp.status_code == 429:
        raise LLMRateLimitError("Anthropic rate limit exceeded")
    if resp.status_code >= 400:
        raise LLMError(f"Anthropic API error: {resp.status_code} {resp.text[:200]}")

    data = resp.json()
    text = data.get("content", [{}])[0].get("text")
    usage = data.get("usage", {})
    return {
        "content": text or "Maaf, saya tidak dapat menjawab saat ini.",
        "usage": {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
        },
    }


PROVIDER_HANDLERS: dict[str, Any] = {
    "gemini": lambda api_key, model, messages, temperature, max_tokens: _call_gemini(
        api_key, model, messages, temperature, max_tokens
    ),
    "openai": lambda api_key, model, messages, temperature, max_tokens: _call_openai_compat(
        api_key,
        "https://api.openai.com/v1/chat/completions",
        model,
        messages,
        temperature,
        max_tokens,
    ),
    "groq": lambda api_key, model, messages, temperature, max_tokens: _call_openai_compat(
        api_key,
        "https://api.groq.com/openai/v1/chat/completions",
        model,
        messages,
        temperature,
        max_tokens,
    ),
    "anthropic": lambda api_key, model, messages, temperature, max_tokens: _call_anthropic(
        api_key, model, messages, temperature, max_tokens
    ),
}


async def chat(
    provider: str,
    model: str | None = None,
    messages: list[dict[str, str]] | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Send messages to an LLM provider and return the response.

    Args:
        provider: One of 'gemini', 'openai', 'anthropic', 'groq'.
        model: Model name override (uses default if omitted).
        messages: List of message dicts with 'role' and 'content'.
        temperature: Sampling temperature.
        max_tokens: Maximum output tokens.

    Returns:
        Dict with keys: content, provider, model, usage.

    Raises:
        LLMConfigError: If provider is unsupported or API key is missing.
        LLMRateLimitError: If provider rate-limits the request.
        LLMError: On provider API failure.
    """
    if not messages:
        raise LLMConfigError("No messages provided")

    handler = PROVIDER_HANDLERS.get(provider)
    if not handler:
        raise LLMConfigError(f"Unsupported provider: {provider}")

    api_key = _get_api_key(provider)
    resolved_model = model or DEFAULT_MODELS.get(provider, "")
    if not resolved_model:
        raise LLMConfigError(f"No default model for provider {provider}")

    start = time.perf_counter()
    try:
        result = await handler(api_key, resolved_model, messages, temperature, max_tokens)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "LLM: provider=%s model=%s latency=%.0fms status=ok",
            provider,
            resolved_model,
            elapsed,
        )
        return {
            "content": result["content"],
            "provider": provider,
            "model": resolved_model,
            "usage": result.get("usage"),
        }
    except (LLMConfigError, LLMRateLimitError, LLMError):
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "LLM: provider=%s model=%s latency=%.0fms status=error",
            provider,
            resolved_model,
            elapsed,
        )
        raise
