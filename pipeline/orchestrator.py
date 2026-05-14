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
from memory.session_store import get_history, add_turn, get_booking_context
from agents.rental_booking_agent import handle_booking_flow

# Intents that should trigger a product search in the database
SEARCH_INTENTS = {"search", "filter", "recommend"}
BOOKING_INTENTS = {"book_initiate", "book_continue", "book_confirm", "book_cancel"}


async def run_chat_pipeline(query: str, session_id: str = "default", user_id: str = None, auth_token: str = None) -> dict:
    start_time = time.time()

    # 1. Cache check (session-aware key)
    # Skip cache if the session has an active booking/cancel flow
    # to avoid stale cached responses being returned for stateful interactions.
    booking_ctx = get_booking_context(session_id)
    is_active_booking = booking_ctx.state not in ("IDLE", "CONFIRMED", "CANCELLED")

    cache_key = hashlib.md5(f"{session_id}:{query}".encode("utf-8")).hexdigest()
    if not is_active_booking:
        cached = get_cached(cache_key)
        if cached:
            cached["cached"] = True
            cached["latency_ms"] = int((time.time() - start_time) * 1000)
            return cached

    # 2. Retrieve conversation history for this session
    chat_history = get_history(session_id)

    # 4. Parallel: Intent + Context-aware Entity extraction
    parallel_agents = RunnableParallel({
        "intent_result": RunnableLambda(lambda q: classify_intent(q, booking_ctx.state)),
        "entities":      RunnableLambda(lambda q: extract_entities(q, chat_history)),
    })
    parallel_result = parallel_agents.invoke(query)

    intent   = parallel_result["intent_result"].get("intent", "search")
    entities = parallel_result["entities"]

    # 5. Routing based on intent and state
    booking_action = None

    # Escape hatch: if user sends a non-booking intent while stuck in a booking state,
    # reset the booking context so they're not trapped forever.
    ESCAPE_INTENTS = {"greet", "search", "filter", "recommend", "out_of_scope"}
    if booking_ctx.state not in ("IDLE", "CONFIRMED", "CANCELLED") and intent in ESCAPE_INTENTS:
        from memory.session_store import reset_booking_context
        reset_booking_context(session_id)
        booking_ctx = get_booking_context(session_id)  # refresh to IDLE

    if intent in BOOKING_INTENTS or booking_ctx.state not in ("IDLE", "CONFIRMED", "CANCELLED"):
        # First, run a DB search if we are initiating booking and we need product context
        if intent == "book_initiate" and booking_ctx.state == "IDLE":
            sql_query, sql_params = build_sql(entities)
            try:
                raw_products = execute_query(sql_query, sql_params)
            except Exception as e:
                raw_products = []
            ranked_products = rank_products(raw_products, entities)
        else:
            ranked_products = [] # Context already holds product, or we don't need a DB search

        booking_result = await handle_booking_flow(
            session_id=session_id,
            user_query=query,
            intent=intent,
            search_entities=entities,
            products=ranked_products,
            user_id=user_id,
            auth_token=auth_token,
            chat_history=chat_history
        )
        final_answer = booking_result["agent_message"]
        _state_to_input = {
            "AWAITING_DATES": "dates",
            "AWAITING_DELIVERY_METHOD": "delivery",
            "AWAITING_ADDRESS": "address",
            "AWAITING_CONFIRMATION": "confirmation",
        }
        booking_action = {
            "state": booking_result["state"],
            "order_id": booking_result["order_id"],
            "requires_input": _state_to_input.get(booking_result["state"]),
            "summary": booking_result["summary"]
        }
        
    elif intent in SEARCH_INTENTS:
        sql_query, sql_params = build_sql(entities)
        try:
            raw_products = execute_query(sql_query, sql_params)
        except Exception as e:
            print(f"[Orchestrator] SQL Error: {e}")
            raw_products = []
        ranked_products = rank_products(raw_products, entities)
        final_answer = generate_response(query, intent, ranked_products, chat_history=chat_history)
    else:
        ranked_products = []
        final_answer = generate_response(query, intent, ranked_products, chat_history=chat_history)

    # 6. Save this turn to session memory
    add_turn(session_id, query, final_answer)

    latency_ms = int((time.time() - start_time) * 1000)

    # 7. Format into response schema
    response_dict = format_chat_response(
        final_answer, 
        intent, 
        ranked_products, 
        latency_ms, 
        cached=False,
        booking_action=booking_action
    )

    # 8. Cache (only for pure search responses, never for booking/cancel flows)
    if booking_action is None:
        set_cache(cache_key, response_dict.copy())
    return response_dict
