# /chat load test

Measures the effect of making the chat pipeline truly async (Nov 2026).

## What changed

| Before | After |
|---|---|
| `RunnableParallel(...).invoke()` for intent + entities inside `async def` | `asyncio.gather(aclassify_intent(...), aextract_entities(...))` with `ainvoke` |
| `generate_response`, `answer_platform_question`, `extract_booking_entities` with sync `.invoke()` | async versions with `ainvoke` |
| `execute_query` (sync pyodbc) called directly in `async def` (`/chat`, `/search`, `/products/{id}`, booking availability check) | `await asyncio.to_thread(execute_query, ...)` |
| `llama-3.1-8b-instant` / `llama-3.3-70b-versatile` (removed by Groq, every call returned 404) | `openai/gpt-oss-20b` / `openai/gpt-oss-120b`, configured once in `agents/llm_config.py` |

## How it is measured

`python benchmarks/run_benchmark.py --llm fake --users 10 --rounds 3`

- Starts the app in-process on port 8010.
- **Fake LLM** (`benchmarks/fake_llm.py`): Groq is replaced by a stub with fixed latency
  (intent 0.4 s, entities 0.6 s, response 1.0 s). The sync path sleeps with `time.sleep`
  (blocks like a real HTTP call), the async path with `asyncio.sleep`.
  Reason: Groq's free tier allows 8,000 tokens/min per model and one `/chat` uses ~3-4k,
  so a concurrent test against real Groq measures 429 back-off, not the server.
- **Database is real** (remote SQL Server, ~0.2 s per query).
- Every request uses a new `session_id`, so the response cache never hits.
- 1 warm-up request, 5 single-user requests, then 3 rounds of 10 simultaneous users.
- A probe hits `GET /` every 100 ms during each round: its latency shows whether the event loop is blocked.

## Results (fake LLM, real DB, 10 concurrent users, 3 rounds)

| Metric | Before | After |
|---|---|---|
| Single user, median | 1.83 s | 1.82 s |
| 10 users, total time (median of 3 rounds) | 18.25 s | 2.78 s (6.6x faster) |
| 10 users, slowest request | 18.53 s | 2.89 s |
| Trivial request during the load, worst case | 18.42 s | 0.01 s |
| Errors | 0 | 0 |

Single-user latency does not change: intent and entities already ran in parallel (threads).
The gain is for concurrent users: before, one request held the event loop for its whole
LLM + DB time, so 10 users were served one after another (~10 x 1.8 s).

## Real Groq, single user (after the fix)

5 requests, 25 s apart to stay under the token limit: median **2.76 s** (1.75-4.11 s).
