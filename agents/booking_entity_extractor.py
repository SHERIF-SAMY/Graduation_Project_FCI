import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Fast model for entity extraction
_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Load prompt from file
_prompt_text = (PROMPTS_DIR / "booking_entity_prompt.txt").read_text(encoding="utf-8")

# Chain WITH MessagesPlaceholder so it can resolve references
_chain = (
    ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a booking entity extraction module for an Arabic/English rental marketplace. "
            "You have access to the conversation history to resolve context. "
            "Always output strictly valid JSON only — no markdown, no explanation."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", _prompt_text),
    ])
    | _llm
    | JsonOutputParser()
)

def extract_booking_entities(query: str, chat_history: list = None) -> dict:
    """
    Extracts booking entities (dates, address, delivery method, confirmation) from the user query.
    Uses conversation history to resolve references.
    """
    try:
        today_str = date.today().isoformat()
        result = _chain.invoke({
            "user_query": query,
            "today": today_str,
            "chat_history": chat_history or [],
        })
        return result if isinstance(result, dict) else {}
    except Exception as e:
        print(f"[BookingEntityExtractor] Error: {e}")
        return {}
