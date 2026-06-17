import json

from src.utils import redis_store


class FakeRedis:
    def __init__(self):
        self.items = []

    def lpush(self, key, value):
        self.items.insert(0, value)

    def ltrim(self, key, start, end):
        self.items = self.items[start : end + 1]

    def lrange(self, key, start, end):
        return self.items[start : end + 1]

    def ping(self):
        return True


def test_push_and_load_latest_readings(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_store, "get_redis_client", lambda: fake)

    redis_store.push_reading({"timestamp": "1", "voltage_kv": 110}, max_records=2)
    redis_store.push_reading({"timestamp": "2", "voltage_kv": 111}, max_records=2)
    redis_store.push_reading({"timestamp": "3", "voltage_kv": 112}, max_records=2)

    assert [record["timestamp"] for record in redis_store.load_latest_readings(max_records=2)] == [
        "2",
        "3",
    ]
    assert json.loads(fake.items[0])["timestamp"] == "3"
