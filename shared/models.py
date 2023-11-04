from enum import Enum
from uuid import UUID

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


class Database(BaseModel):
    source_id: UUID
    display_name: str
    conn_string: str
    inactive: bool


class AlertType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    FREE_SPACE = "free_space"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    ACTIVE_PEERS = "active_peers"
    LWLOCK_COUNT = "lwlock_count"
    BAD_CONN_STING = "bad_conn_string"


class Alert(BaseModel):
    type: AlertType
    message: str
    # TODO: Set the correct type
    fields: list
