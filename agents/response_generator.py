import os
import json
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# High-quality model for final response generation
_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.environ.get("GROQ_API_KEY"),
)

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


def generate_response(
    query: str,
    intent: str,
    ranked_products: list,
    chat_history: list = None,          # ← List of LangChain HumanMessage/AIMessage
) -> str:
    """
    Generates the final natural language response using llama-3.3-70b-versatile.
    Injects conversation history into the prompt via MessagesPlaceholder.
    """
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

    try:
        return _chain.invoke({
            "user_query": query,
            "intent": intent,
            "formatted_sql_results": json.dumps(
                filtered_products, indent=2, ensure_ascii=False, default=_decimal_serializer
            ),
            "chat_history": chat_history or [],   # ← pass empty list if no history
        })
    except Exception as e:
        print(f"[ResponseGenerator] Error: {e}")
        return "Sorry, I had an error generating my response."
