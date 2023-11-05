import json

from pydantic import BaseModel


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config_data = json.load(f)
            return super().__init__(**config_data)

    class Config:
        populate_by_name = True


class DatabaseCredentials(BaseModel):
    driver: str
    username: str
    password: str
    url: str
    port: int
    db_name: str


class RedisCredentials(BaseModel):
    username: str
    password: str
    host: str
    port: int


class MetricsLimits(BaseModel):
    cpu_usage_threshold: float
    free_space_threshold: float
    ram_usage_threshold: float
    max_active_peers: int
    max_active_peers_delta: float
    max_active_peers_ratio: float
    max_transaction_duration: float
    max_lwlock_count: int


class WatchdogSettings(BaseModel):
    disable_healthcheck: bool
    interval: int


class SharedResources(JSONSettings):
    pg_creds: DatabaseCredentials
    watchdog: WatchdogSettings
    redis_creds: RedisCredentials
    metrics: MetricsLimits
