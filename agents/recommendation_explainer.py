import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from recommendation.models import UserProfile

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.environ.get("GROQ_API_KEY"),
)

_prompt_text = (PROMPTS_DIR / "recommendation_prompt.txt").read_text(encoding="utf-8")

_chain = (
    ChatPromptTemplate.from_messages([
        ("system", _prompt_text),
    ])
    | _llm
    | StrOutputParser()
)

EXPLANATION_TIMEOUT = 8.0  # seconds

def _fallback_message(lang: str) -> str:
    if lang == "ar":
        return "إليك أفضل المنتجات المتاحة بناءً على اهتماماتك."
    return "Here are the top available products based on your interests."

def _sync_explain(profile: UserProfile, products: list[dict], rec_type: str) -> str:
    product_summaries = []
    for p in products:
        reasons = ", ".join(p.get("_match_reasons", []))
        source = p.get("_recommendation_source", "unknown")
        price = p.get("FinalPricePerDay", p.get("PricePerDay", "N/A"))
        summary = f"- {p.get('Name', 'Product')} (Price: {price}): Match reasons: {reasons}. Source: {source}"
        product_summaries.append(summary)
        
    try:
        return _chain.invoke({
            "favorite_brand": profile.favorite_brand or "None",
            "favorite_category": profile.favorite_category or "None",
            "preferred_location": profile.preferred_location or "None",
            "average_budget": profile.average_budget or "None",
            "top_keywords": ", ".join(profile.top_keywords) if profile.top_keywords else "None",
            "profile_confidence": profile.profile_confidence,
            "products_with_reasons": "\n".join(product_summaries) or "No products",
            "recommendation_type": rec_type,
            "language_hint": "ar" if profile.preferred_language == "ar" else "en"
        })
    except Exception as e:
        print(f"[RecommendationExplainer] Sync LLM failed: {e}")
        return _fallback_message(profile.preferred_language)

async def generate_recommendation_explanation(
    profile: UserProfile,
    products: list[dict],
    rec_type: str,
) -> str:
    if rec_type == "cold_start":
        return ""   # no confusing explanation for new users

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_sync_explain, profile, products, rec_type),
            timeout=EXPLANATION_TIMEOUT,
        )
    except (asyncio.TimeoutError, Exception) as e:
        print(f"[RecommendationExplainer] fallback — {e}")
        return _fallback_message(profile.preferred_language)
