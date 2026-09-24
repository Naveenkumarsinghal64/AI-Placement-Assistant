import json
from typing import Optional

from google import genai
from google.genai import types

from app.config import EMBEDDING_MODEL, GEMINI_API_KEY, GEMINI_MODEL

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def generate_text(prompt: str, temperature: float = 0.4) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return response.text.strip()


def generate_json(prompt: str, temperature: float = 0.3) -> dict:
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    raw = response.text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    client = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type.upper()),
    )
    return response.embeddings[0].values
