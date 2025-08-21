import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL)

def get_rosters(session_id: str):
    data = redis_client.get(f"roster:{session_id}")
    if data:
        return json.loads(data)
    return {}

def save_rosters(session_id: str, roster):
    redis_client.set(f"roster:{session_id}", json.dumps(roster))
