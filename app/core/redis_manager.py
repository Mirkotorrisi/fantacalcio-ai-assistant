import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "your_default_password")

redis_client = redis.Redis(
    host=REDIS_URL,
    port=REDIS_PORT,
    decode_responses=True,
    username="default",
    password=REDIS_PASSWORD
)

def get_rosters(session_id: str):
    print("retrieving rosters for session:", session_id)
    print(f"roster:{session_id}")
    data = redis_client.get(f"roster:{session_id}")
    if data:
        return json.loads(data)
    return {}

def save_rosters(session_id: str, roster):
    redis_client.set(f"roster:{session_id}", json.dumps(roster))
