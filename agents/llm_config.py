"""Single place for Groq model names, so a model deprecation is a one-line change.

Groq removed llama-3.1-8b-instant and llama-3.3-70b-versatile; every agent returned 404.
Override with GROQ_FAST_MODEL / GROQ_SMART_MODEL in .env.
"""
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

FAST_MODEL = os.environ.get("GROQ_FAST_MODEL", "openai/gpt-oss-20b")    # intent, entities, FAQ
SMART_MODEL = os.environ.get("GROQ_SMART_MODEL", "openai/gpt-oss-120b")  # final answers


def make_llm(model: str, temperature: float = 0) -> ChatGroq:
    extra = {}
    if model.startswith("openai/gpt-oss"):
        extra["reasoning_effort"] = "low"  # short hidden reasoning keeps latency low
    return ChatGroq(
        model=model,
        temperature=temperature,
        api_key=os.environ.get("GROQ_API_KEY"),
        **extra,
    )
