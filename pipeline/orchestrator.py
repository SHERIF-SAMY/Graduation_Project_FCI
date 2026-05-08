import time
import hashlib
from langchain_core.runnables import RunnableParallel, RunnableLambda

from agents.intent_agent import classify_intent
from agents.entity_extractor import extract_entities
from agents.sql_builder import build_sql
from sql.executor import execute_query
from ranking.ranker import rank_products
from agents.response_generator import generate_response
from cache.query_cache import get_cached, set_cache
from formatter.response_formatter import format_chat_response
from memory.session_store import get_history, add_turn


async def run_chat_pipeline(query: str, session_id: str = "default") -> dict:
    start_time = time.time()

    # 1. Cache check (session-aware key)
    cache_key = hashlib.md5(f"{session_id}:{query}".encode("utf-8")).hexdigest()
    cached = get_cached(cache_key)
    if cached:
        cached["cached"] = True
        cached["latency_ms"] = int((time.time() - start_time) * 1000)
        return cached

    # 2. Retrieve conversation history for this session
    chat_history = get_history(session_id)

    # 3. Parallel: Intent + Context-aware Entity extraction
    # Both agents now receive the chat_history so they can resolve
    # references like "it", "that one", "the same product"
    parallel_agents = RunnableParallel({
        "intent_result": RunnableLambda(lambda q: classify_intent(q)),
        "entities":      RunnableLambda(lambda q: extract_entities(q, chat_history)),
    })
    parallel_result = parallel_agents.invoke(query)

    intent   = parallel_result["intent_result"].get("intent", "search")
    entities = parallel_result["entities"]

    # 4. Build parameterized SQL from entities
    sql_query, sql_params = build_sql(entities)

    # 5. Execute SQL query against Products_LLm view
    try:
        raw_products = execute_query(sql_query, sql_params)
    except Exception as e:
        print(f"[Orchestrator] SQL Error: {e}")
        raw_products = []

    # 6. Rank Results (top 5)
    ranked_products = rank_products(raw_products, entities)

    # 7. Generate final response with full conversation history
    final_answer = generate_response(query, intent, ranked_products, chat_history=chat_history)

    # 8. Save this turn to session memory
    add_turn(session_id, query, final_answer)

    latency_ms = int((time.time() - start_time) * 1000)

    # 9. Format into response schema
    response_dict = format_chat_response(final_answer, intent, ranked_products, latency_ms, cached=False)

    # 10. Cache and return
    set_cache(cache_key, response_dict.copy())
    return response_dict
