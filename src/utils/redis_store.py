import json
import os
from pathlib import Path


DEFAULT_TELEMETRY_KEY = "substation:telemetry"
MAX_RECORDS = 300


def load_dotenv(path=".env"):
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def redis_configured():
    load_dotenv()
    return bool(
        os.getenv("UPSTASH_REDIS_HOST")
        and os.getenv("UPSTASH_REDIS_PORT")
        and os.getenv("UPSTASH_REDIS_PASSWORD")
    )


def get_redis_client():
    load_dotenv()
    if not redis_configured():
        return None

    try:
        import redis
    except ImportError as exc:
        raise RuntimeError(
            "Redis is configured, but the 'redis' Python package is not installed. "
            "Run: pip install redis"
        ) from exc

    return redis.Redis(
        host=os.getenv("UPSTASH_REDIS_HOST"),
        port=int(os.getenv("UPSTASH_REDIS_PORT", "6379")),
        password=os.getenv("UPSTASH_REDIS_PASSWORD"),
        ssl=True,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
    )


def push_reading(reading, key=DEFAULT_TELEMETRY_KEY, max_records=MAX_RECORDS):
    try:
        client = get_redis_client()
    except RuntimeError:
        return False

    if client is None:
        return False

    try:
        client.lpush(key, json.dumps(reading))
        client.ltrim(key, 0, max_records - 1)
    except Exception:
        return False
    return True


def load_latest_readings(key=DEFAULT_TELEMETRY_KEY, max_records=MAX_RECORDS):
    try:
        client = get_redis_client()
    except RuntimeError:
        return []

    if client is None:
        return []

    try:
        raw_records = client.lrange(key, 0, max_records - 1)
    except Exception:
        return []

    records = [json.loads(item) for item in raw_records]
    records.reverse()
    return records


def redis_status():
    if not redis_configured():
        return "Local Mode"

    try:
        client = get_redis_client()
    except RuntimeError:
        return "Redis Package Missing"

    try:
        client.ping()
    except Exception:
        return "Redis Offline"
    return "Redis Online"
