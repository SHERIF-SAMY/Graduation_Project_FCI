import os
from pathlib import Path
from dotenv import load_dotenv
from agents.llm_config import FAST_MODEL, make_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Fast model for intent classification
_llm = make_llm(FAST_MODEL)

# Load prompt from file
_prompt_text = (PROMPTS_DIR / "intent_prompt.txt").read_text(encoding="utf-8")

# LangChain chain: Prompt → LLM → JSON output
_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are an intent classifier. Always respond with valid JSON only."),
        ("human", _prompt_text),
    ])
    | _llm
    | JsonOutputParser()
)


def classify_intent(query: str, booking_state: str = "IDLE") -> dict:
    """Classifies user intent with the fast Groq model via LangChain."""
    try:
        result = _chain.invoke({
            "user_query": query,
            "booking_state": booking_state
        })
        return result if isinstance(result, dict) else {"intent": "search", "confidence": 0.5}
    except Exception as e:
        print(f"[IntentAgent] Error: {e}")
        return {"intent": "search", "confidence": 0.0}


async def aclassify_intent(query: str, booking_state: str = "IDLE") -> dict:
    """Async version for the chat pipeline: frees the event loop while Groq answers."""
    try:
        result = await _chain.ainvoke({
            "user_query": query,
            "booking_state": booking_state
        })
        return result if isinstance(result, dict) else {"intent": "search", "confidence": 0.5}
    except Exception as e:
        print(f"[IntentAgent] Error: {e}")
        return {"intent": "search", "confidence": 0.0}
