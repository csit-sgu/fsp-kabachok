import os

from shared.models import (
    Action,
    BaseManagingRequest,
    MaxConnectionsBody,
    SharedBuffersBody,
    TerminateProcessBody,
)

ACTION_BODY_MAPPING = {
    Action.SET_MAX_CONNECTIONS: MaxConnectionsBody,
    Action.SET_SHARED_BUFFERS: SharedBuffersBody,
    Action.TERMINATE_PROCESS: TerminateProcessBody,
    Action.RESTART_SERVER: BaseManagingRequest,
}


SHARED_CONFIG_PATH = os.getenv("SHARED_CONFIG_PATH", "../config")
