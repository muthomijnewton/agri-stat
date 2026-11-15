"""Bounded external reads, with optional shared Redis response caching."""
import hashlib
import json
import os
import httpx


def fetch_json(url, *, params=None, data=None, cache_seconds=3600):
    key = "agristat:external:" + hashlib.sha256(
        json.dumps([url, params, data], sort_keys=True).encode()
    ).hexdigest()
    cache = None
    if cache_seconds > 0 and os.getenv("REDIS_URL"):
        try:
            from redis import Redis
            cache = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=2, socket_connect_timeout=2)
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
        except (ImportError, OSError, ValueError):
            cache = None
        except Exception:
            # Redis is an optimization, not an external-data availability gate.
            cache = None
    with httpx.Client(timeout=60, headers={"User-Agent": os.getenv("EXTERNAL_DATA_USER_AGENT", "AgricStatDash/1.0 (https://github.com/muthomijnewton/agri-stat)")}) as client:
        with client.stream("POST" if data else "GET", url, params=params, data=data) as response:
            response.raise_for_status()
            content = bytearray()
            for part in response.iter_bytes():
                content.extend(part)
                if len(content) > 10 * 1024 * 1024:
                    raise ValueError("External response exceeds 10 MB")
            result = json.loads(content)
    if cache:
        try:
            cache.setex(key, cache_seconds, json.dumps(result))
        except Exception:
            pass
    return result
