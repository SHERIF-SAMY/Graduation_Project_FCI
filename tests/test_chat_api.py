"""Tests for POST /chat.

Run from the repo root:
    python -m pytest tests -v

No Groq and no database: every external call is replaced by a fake with monkeypatch,
so the tests are fast, free, and give the same result every run.

Mutation check (proves the concurrency test can fail): set SIMULATE_BLOCKING=1 and the
fake LLM calls use time.sleep instead of asyncio.sleep, like a sync .invoke() inside async def.
"""
import asyncio
import os
import time
import uuid

os.environ.setdefault("GROQ_API_KEY", "test-key")  # agents build ChatGroq clients at import time

import httpx
import pytest
from fastapi.testclient import TestClient

import main
from pipeline import orchestrator

LLM_DELAY_S = {"intent": 0.2, "entities": 0.3, "response": 0.5}
DB_DELAY_S = 0.05
BLOCKING = os.environ.get("SIMULATE_BLOCKING") == "1"

FAKE_ROWS = [
    {"Id": 1, "Name": "Canon EOS 250D", "CategoryName": "Cameras", "Brand": "Canon",
     "Condition": 1, "PricePerDay": 300, "LocationArea": "Cairo", "RentalGuarantee": 1, "Status": 1},
    {"Id": 2, "Name": "Nikon D3500", "CategoryName": "Cameras", "Brand": "Nikon",
     "Condition": 2, "PricePerDay": 250, "LocationArea": "Giza", "RentalGuarantee": 0, "Status": 1},
]


async def llm_wait(seconds: float) -> None:
    if BLOCKING:
        time.sleep(seconds)  # the bug test 3 must catch: freezes the event loop
    else:
        await asyncio.sleep(seconds)  # a real async HTTP call: frees the loop while waiting


def new_session() -> str:
    # a fresh session per request: no shared history, and the response cache never hits
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def fake_backend(monkeypatch):
    """Replace Groq, the database and the interaction logger. Returns the list of calls made."""
    calls = []

    async def fake_intent(query, booking_state):
        calls.append("intent")
        await llm_wait(LLM_DELAY_S["intent"])
        return {"intent": "search", "confidence": 0.9}

    async def fake_entities(query, chat_history):
        calls.append("entities")
        await llm_wait(LLM_DELAY_S["entities"])
        return {"category": "camera"}

    async def fake_response(query, intent, products, chat_history=None):
        calls.append("response")
        await llm_wait(LLM_DELAY_S["response"])
        return f"Found {len(products)} cameras."

    def fake_db(sql, params):
        calls.append("db")
        time.sleep(DB_DELAY_S)  # sync, like pyodbc; the app runs it with asyncio.to_thread
        return [dict(row) for row in FAKE_ROWS]

    async def no_log(*args, **kwargs):
        return None

    # Patch the name where it is LOOKED UP (pipeline.orchestrator / main), not where it is defined.
    monkeypatch.setattr(orchestrator, "aclassify_intent", fake_intent)
    monkeypatch.setattr(orchestrator, "aextract_entities", fake_entities)
    monkeypatch.setattr(orchestrator, "agenerate_response", fake_response)
    monkeypatch.setattr(orchestrator, "execute_query", fake_db)
    monkeypatch.setattr(main, "log_interaction", no_log)
    return calls


@pytest.fixture
def anyio_backend():
    return "asyncio"


# 1. Validation: a bad request never reaches the pipeline.
def test_chat_without_query_returns_422(fake_backend):
    client = TestClient(main.app)

    r = client.post("/chat", json={"session_id": new_session()})

    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "query"]
    assert fake_backend == []  # no LLM or DB call was made


# 2. Happy path: a search returns the products from the DB and the LLM's answer.
def test_chat_search_returns_products_and_answer(fake_backend):
    client = TestClient(main.app)

    r = client.post("/chat", json={"query": "I want a camera", "session_id": new_session()})

    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "search"
    assert body["total_found"] == 2
    assert {p["name"] for p in body["products"]} == {"Canon EOS 250D", "Nikon D3500"}
    assert body["answer"] == "Found 2 cameras."
    assert body["cached"] is False
    assert sorted(fake_backend) == ["db", "entities", "intent", "response"]


# 3. Concurrency: 5 users at once take about as long as 1 user (the Day 4 fix).
@pytest.mark.anyio
async def test_concurrent_chats_do_not_block_each_other(fake_backend):
    users = 5
    one_request = max(LLM_DELAY_S["intent"], LLM_DELAY_S["entities"]) + DB_DELAY_S + LLM_DELAY_S["response"]

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        responses = await asyncio.gather(*(
            client.post("/chat", json={"query": "I want a camera", "session_id": new_session()})
            for _ in range(users)
        ))
        total = time.perf_counter() - start

    assert [r.status_code for r in responses] == [200] * users
    # concurrent: ~one_request (0.85s). Blocked event loop: ~users * one_request (4.25s).
    assert total < 2 * one_request, f"{users} requests took {total:.2f}s; one takes ~{one_request:.2f}s"
