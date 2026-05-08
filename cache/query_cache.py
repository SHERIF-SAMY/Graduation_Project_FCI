import time

cache = {}
TTL = 300  # 5 minutes

def get_cached(query_hash: str):
    if query_hash in cache:
        ts, result = cache[query_hash]
        if time.time() - ts < TTL:
            return result
    return None

def set_cache(query_hash: str, result: dict):
    cache[query_hash] = (time.time(), result)
