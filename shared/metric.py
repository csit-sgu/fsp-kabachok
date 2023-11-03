from enum import Enum


class MetricType(Enum):
    CPU_USAGE = "cpu_usage"
    FREE_SPACE = "free_space"
    ACTIVE_PEERS = "active_peers"
    LWLOCK_TRANSACTIONS = "lwlock_transactions"
    LONGEST_TRANSACTION = "longest_transaction"


class Metric:
    def __init__(self, type: MetricType, value: float):
        self.type = type
        self.value = value
