import os
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError

from app.core.ai_errors import AIServiceUnavailable

load_dotenv()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceUnavailable("AI processing is not configured on this server")
    return OpenAI(api_key=api_key)


def create_chat_completion(**kwargs: Any):
    try:
        return get_client().chat.completions.create(**kwargs)
    except (AuthenticationError, RateLimitError, APIConnectionError, APIStatusError) as exc:
        # Provider response bodies can contain sensitive implementation details.
        raise AIServiceUnavailable("The configured AI service is unavailable. Please contact the administrator.") from exc
