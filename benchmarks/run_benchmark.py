"""Start the app in-process, run the load test, stop the app.

    python benchmarks/run_benchmark.py --llm fake --users 10 --rounds 3
    python benchmarks/run_benchmark.py --llm real --users 1 --rounds 0 --singles 5
"""
import argparse
import asyncio
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", choices=["fake", "real"], default="fake")
    ap.add_argument("--users", type=int, default=10)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--singles", type=int, default=5)
    ap.add_argument("--port", type=int, default=8010)
    a = ap.parse_args()

    if a.llm == "fake":
        from benchmarks import fake_llm
        fake_llm.install()

    import uvicorn
    from benchmarks import load_test
    from main import app

    server = uvicorn.Server(uvicorn.Config(app, port=a.port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.2)
    pause = 0 if a.llm == "fake" else 60
    try:
        asyncio.run(load_test.run(f"http://127.0.0.1:{a.port}", a.users, a.rounds, a.singles, pause))
    finally:
        server.should_exit = True
        thread.join(10)


if __name__ == "__main__":
    main()
