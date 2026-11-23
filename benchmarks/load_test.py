"""Load test for the RentHub /chat endpoint.

Measures:
  1. single-user latency: one /chat search request at a time (median of N)
  2. concurrent latency: U users send a /chat request at the same moment
  3. event-loop health: while (2) runs, a probe hits a trivial endpoint every 100 ms.
     If the loop is blocked by sync I/O, the probe's latency jumps.

Every request uses a fresh session_id, so the response cache never hits.

Usage (server already running):
    python benchmarks/load_test.py --base http://127.0.0.1:8010 --users 5 --rounds 3
"""
import argparse
import asyncio
import statistics
import time
import uuid

import httpx

QUERIES = [
    "I want to rent a camera in Cairo",
    "عايز اأجر لابتوب جديد",
    "show me cheap drills under 200 per day",
    "عايز بلايستيشن في مدينة نصر",
    "do you have bikes for rent?",
]


async def chat_once(client: httpx.AsyncClient, base: str, query: str) -> dict:
    start = time.perf_counter()
    r = await client.post(f"{base}/chat", json={"query": query, "session_id": f"bench-{uuid.uuid4().hex[:10]}"})
    elapsed = time.perf_counter() - start
    body = r.json() if r.status_code == 200 else {}
    return {"s": elapsed, "status": r.status_code, "intent": body.get("intent"),
            "products": len(body.get("products") or []), "server_ms": body.get("latency_ms"),
            "answer": (body.get("answer") or "")[:80]}


async def probe(client: httpx.AsyncClient, base: str, stop: asyncio.Event, out: list) -> None:
    while not stop.is_set():
        start = time.perf_counter()
        await client.get(f"{base}/", follow_redirects=False)
        out.append(time.perf_counter() - start)
        await asyncio.sleep(0.1)


def pct(values: list, p: float) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p * (len(values) - 1))))]


async def run(base: str, users: int, rounds: int, singles: int, pause: float) -> dict:
    limits = httpx.Limits(max_connections=100)
    async with httpx.AsyncClient(timeout=120, limits=limits) as client:
        await chat_once(client, base, "hello")  # warm-up: connections, model clients

        single = []
        for i in range(singles):
            single.append(await chat_once(client, base, QUERIES[i % len(QUERIES)]))
        print("single-user:", " ".join(f"{x['s']:.2f}s" for x in single))
        for x in single:
            print(f"  {x['status']} intent={x['intent']} products={x['products']} answer={x['answer']!r}")

        conc_totals, conc_lat, probe_lat, errors = [], [], [], 0
        for rnd in range(rounds):
            await asyncio.sleep(pause)  # stay under Groq's per-minute rate limit
            stop, probes = asyncio.Event(), []
            probe_task = asyncio.create_task(probe(client, base, stop, probes))
            start = time.perf_counter()
            res = await asyncio.gather(*(chat_once(client, base, QUERIES[i % len(QUERIES)]) for i in range(users)))
            total = time.perf_counter() - start
            stop.set()
            await probe_task
            conc_totals.append(total)
            conc_lat += [x["s"] for x in res]
            probe_lat += probes
            errors += sum(x["status"] != 200 for x in res)
            print(f"round {rnd + 1}: {users} users total={total:.2f}s "
                  f"latencies={[round(x['s'], 2) for x in res]} probe_max={max(probes):.2f}s "
                  f"intents={[x['intent'] for x in res]}")

    summary = {"single_median_s": statistics.median(x["s"] for x in single)}
    if not conc_totals:
        print(f"\nSUMMARY\n  single_median_s              {summary['single_median_s']:.2f}")
        return summary
    summary |= {
        "concurrent_total_median_s": statistics.median(conc_totals),
        "concurrent_p50_s": pct(conc_lat, 0.5),
        "concurrent_max_s": max(conc_lat),
        "probe_p50_s": pct(probe_lat, 0.5),
        "probe_max_s": max(probe_lat),
        "errors": errors,
    }
    print("\nSUMMARY")
    for k, v in summary.items():
        print(f"  {k:<28} {v:.2f}" if isinstance(v, float) else f"  {k:<28} {v}")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8010")
    ap.add_argument("--users", type=int, default=5)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--singles", type=int, default=5)
    ap.add_argument("--pause", type=float, default=20)
    a = ap.parse_args()
    asyncio.run(run(a.base, a.users, a.rounds, a.singles, a.pause))


if __name__ == "__main__":
    main()
