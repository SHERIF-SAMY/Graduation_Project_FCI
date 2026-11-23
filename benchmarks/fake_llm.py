"""Replace Groq with a fake LLM that has fixed, realistic latency.

Why: the Groq free tier allows 8,000 tokens/minute per model, and one /chat uses ~3-4k,
so any concurrent load test against real Groq measures 429 back-off, not our code.
The fake keeps the *shape* of the I/O:
  - sync path (.invoke)   -> time.sleep      (blocks the calling thread, like a real HTTP call)
  - async path (.ainvoke) -> asyncio.sleep   (yields the event loop, like an async HTTP call)
Latencies are the medians measured against real Groq (benchmarks/README.md).
The database stays real.
"""
import asyncio
import json
import time

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_groq import ChatGroq

LATENCY_S = {"intent": 0.4, "entities": 0.6, "response": 1.0, "other": 0.6}


def _kind(messages) -> str:
    system = str(messages[0].content).lower() if messages else ""
    if "intent classifier" in system:
        return "intent"
    if "entity extraction" in system:
        return "entities"
    if "rental" in system or "assistant" in system:
        return "response"
    return "other"


def _reply(kind: str, messages) -> str:
    if kind == "intent":
        return json.dumps({"intent": "search", "confidence": 0.9})
    if kind == "entities":
        return json.dumps({"category": None, "brand": None, "location": None, "max_price": None,
                           "condition": None, "name_keyword": None})
    return "Here are some options that match what you asked for."


def _result(messages) -> tuple[float, ChatResult]:
    kind = _kind(messages)
    msg = AIMessage(content=_reply(kind, messages))
    return LATENCY_S[kind], ChatResult(generations=[ChatGeneration(message=msg)])


def _generate(self, messages, stop=None, run_manager=None, **kwargs):
    delay, result = _result(messages)
    time.sleep(delay)
    return result


async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
    delay, result = _result(messages)
    await asyncio.sleep(delay)
    return result


def install() -> None:
    ChatGroq._generate = _generate
    ChatGroq._agenerate = _agenerate
