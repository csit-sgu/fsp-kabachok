from enum import Enum
from typing import List
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
    LONG_TRANSACTION = "long_transaction"


class Metric(BaseModel):
    type: MetricType
    value: float | None
    context: dict | None = None


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


class Alert(BaseModel):
    type: AlertType
    message: str


class Action(Enum):
    SET_MAX_CONNECTIONS = "set_max_connections"
    SET_SHARED_BUFFERS = "set_shared_buffers"
    TERMINATE_PROCESS = "terminate_process"
    RESTART_SERVER = "restart_server"


class BaseManagingRequest(BaseModel):
    secret: str
    locale: str


class MaxConnectionsBody(BaseManagingRequest):
    max_connections: int


class SharedBuffersBody(BaseManagingRequest):
    shared_buffers: int


class TerminateProcessBody(BaseManagingRequest):
    pids: List[int]
