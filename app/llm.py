"""Single place that builds chat models. The project runs on OpenAI only (`OPENAI_API_KEY`).

    from app.llm import chat_model, llm_available
    if llm_available():
        model = chat_model(max_tokens=1000)        # ChatOpenAI, temperature 0 by default

Vision: pass OpenAI-style image parts `{"type": "image_url", "image_url": {"url": "data:<mime>;base64,<data>"}}`;
`image_part()` builds one from raw bytes.
"""

from __future__ import annotations

import base64

from langchain_openai import ChatOpenAI

from app.config import settings


def llm_available() -> bool:
    return bool(settings.openai_api_key)


def chat_model(*, model: str | None = None, temperature: float = 0.0, max_tokens: int | None = None,
               timeout: int = 60, max_retries: int = 2) -> ChatOpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return ChatOpenAI(model=model or settings.openai_model, api_key=settings.openai_api_key, temperature=temperature,
                      max_tokens=max_tokens, timeout=timeout, max_retries=max_retries)


def image_part(content: bytes, mime_type: str) -> dict:
    return {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64.b64encode(content).decode()}"}}
