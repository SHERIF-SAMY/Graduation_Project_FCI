import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Fast model for intent classification
_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
)

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


def classify_intent(query: str) -> dict:
    """Classifies user intent using llama3-8b-8192 via LangChain."""
    try:
        result = _chain.invoke({"user_query": query})
        return result if isinstance(result, dict) else {"intent": "search", "confidence": 0.5}
    except Exception as e:
        print(f"[IntentAgent] Error: {e}")
        return {"intent": "search", "confidence": 0.0}
