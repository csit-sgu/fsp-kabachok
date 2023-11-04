from enum import Enum

from pydantic import BaseModel


class SubmitDatabaseRequest(BaseModel):
    user_id: int
    display_name: str
    conn_string: str


class MetricType(Enum):
    CPU_USAGE = "cpu_usage"
    FREE_SPACE = "free_space"
    ACTIVE_PEERS = "active_peers"
    LWLOCK_TRANSACTIONS = "lwlock_transactions"
    LONGEST_TRANSACTION = "longest_transaction"


class Metric(BaseModel):
    type: MetricType
    value: float | None
