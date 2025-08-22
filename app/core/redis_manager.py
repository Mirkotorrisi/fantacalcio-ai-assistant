import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "your_default_password")

redis_client = redis.Redis(
    host='redis-12223.c17.us-east-1-4.ec2.redns.redis-cloud.com',
    port=12223,
    decode_responses=True,
    username="default",
    password="o5dm9N1Z2zFZxLfQ3gW4gl6QyYE2JrWu",
)

def get_rosters(session_id: str):
    data = redis_client.get(f"roster:{session_id}")
    if data:
        return json.loads(data)
    return {}

def save_rosters(session_id: str, roster):
    redis_client.set(f"roster:{session_id}", json.dumps(roster))
