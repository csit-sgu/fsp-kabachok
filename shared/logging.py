import json
from logging.config import dictConfig

from shared.utils import SHARED_CONFIG_PATH

LOGGING_FORMAT = (
    "[%(levelname)s] [%(asctime)s] %(message)s (%(correlation_id)s)"
)


def configure_logging() -> None:
    with open(f"{SHARED_CONFIG_PATH}/settings.json") as f:
        d = json.load(f)
        dictConfig(d["logger"])
