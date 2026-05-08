import os
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
_prompt_text = (PROMPTS_DIR / "entity_prompt.txt").read_text(encoding="utf-8")

# Chain WITH MessagesPlaceholder so it can resolve references like "it", "that one", "the same"
_chain = (
    ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an entity extraction module for an Arabic/English rental marketplace. "
            "You understand both Arabic and English queries fluently. "
            "You have access to the conversation history to resolve references like 'it', 'that', 'the same one', 'نفسه', 'ده', 'دي'. "
            "CRITICAL: Always output field VALUES in ENGLISH only — translate any Arabic product names, brands, categories, "
            "and locations to English before adding them to the JSON. "
            "For condition: 'جديد'/'جديدة' → 'New'; 'مستعمل'/'مستخدم' → 'Used'. "
            "Always output strictly valid JSON only — no markdown, no explanation.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),  # ← history injected here
        ("human", _prompt_text),
    ])
    | _llm
    | JsonOutputParser()
)


def extract_entities(query: str, chat_history: list = None) -> dict:
    """
    Extracts rental product entities from the user query.
    Uses conversation history to resolve references like 'it', 'that one', 'the same'.
    """
    try:
        result = _chain.invoke({
            "user_query": query,
            "chat_history": chat_history or [],
        })
        return result if isinstance(result, dict) else {}
    except Exception as e:
        print(f"[EntityExtractor] Error: {e}")
        return {}
