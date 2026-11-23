import os
import json
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv
from agents.llm_config import SMART_MODEL, make_llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# High-quality model for final response generation
_llm = make_llm(SMART_MODEL, temperature=0.3)

# Load prompts from files
_system_prompt = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
_response_template = (PROMPTS_DIR / "final_response_prompt.txt").read_text(encoding="utf-8")

# LangChain chain with MessagesPlaceholder for conversation memory
# Flow: System → History → Current user turn → LLM → String
_chain = (
    ChatPromptTemplate.from_messages([
        ("system", _system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),  # ← conversation memory injected here
        ("human", _response_template),
    ])
    | _llm
    | StrOutputParser()
)


def _decimal_serializer(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _build_inputs(query: str, intent: str, ranked_products: list, chat_history: list = None) -> dict:
    """Prompt inputs shared by the sync and async versions."""
    # Filter product fields sent to LLM to reduce tokens
    filtered_products = [
        {
            "Name": p.get("Name"),
            "PricePerDay": float(
                p.get("FinalPricePerDay") if p.get("FinalPricePerDay") is not None 
                else p.get("PricePerDay") if p.get("PricePerDay") is not None 
                else 0
            ),
            "Condition": "New" if p.get("Condition") in (1, "1", "New", "new") else "Used",
            "LocationArea": p.get("LocationArea"),
            "Brand": p.get("Brand"),
        }
        for p in ranked_products
    ]
    return {
        "user_query": query,
        "intent": intent,
        "formatted_sql_results": json.dumps(
            filtered_products, indent=2, ensure_ascii=False, default=_decimal_serializer
        ),
        "chat_history": chat_history or [],   # ← pass empty list if no history
    }


def generate_response(
    query: str,
    intent: str,
    ranked_products: list,
    chat_history: list = None,          # ← List of LangChain HumanMessage/AIMessage
) -> str:
    """
    Generates the final natural language response using the smart Groq model.
    Injects conversation history into the prompt via MessagesPlaceholder.
    """
    try:
        return _chain.invoke(_build_inputs(query, intent, ranked_products, chat_history))
    except Exception as e:
        print(f"[ResponseGenerator] Error: {e}")
        return "Sorry, I had an error generating my response."


async def agenerate_response(
    query: str,
    intent: str,
    ranked_products: list,
    chat_history: list = None,
) -> str:
    """Async version for the chat pipeline: frees the event loop while Groq answers."""
    try:
        return await _chain.ainvoke(_build_inputs(query, intent, ranked_products, chat_history))
    except Exception as e:
        print(f"[ResponseGenerator] Error: {e}")
        return "Sorry, I had an error generating my response."
