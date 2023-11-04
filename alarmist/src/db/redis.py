import datetime
import logging

import redis

from shared.db import Entity
from shared.models import MetricType

logger = logging.getLogger()


class RedisRepository:
    def __init__(self, redis: redis.Redis, metric: MetricType):
        self._redis = redis
        self._table_name = metric.value

    async def add(
        self, source_id: str, timestamp: datetime.time, metrics_value: int
    ):
        logger.debug(f"{source_id} {timestamp} {metrics_value}")
        self._redis.hset(source_id, timestamp, metrics_value)

    async def get(self, source_id: str) -> Entity:
        return self._redis.hgetall(source_id)

    async def cleanup(self):
        now = datetime.now()
        keys = self._redis.execute_command(f"keys *{self._table_name}*")
        for key in keys:
            data = self._redis.hgetall(key)
            for timestamp, value in data.items():
                if now - timestamp > datetime.timedelta(seconds=5):
                    logger.debug(f"delete {key} {self._table_name} {value}")
                    self._redis.hdel(key, value)
