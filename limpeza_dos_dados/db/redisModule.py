import redis
import pandas as pd

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)

    def get(self, key):
        value = self.client.get(key)
        if value:
            return pd.read_json(value)  # Converte de JSON para DataFrame
        return None

    def set(self, key, value, ttl=None):
        self.client.set(key, value.to_json(), ex=ttl)  # Armazena como JSON

    def exists(self, key):
        return self.client.exists(key)