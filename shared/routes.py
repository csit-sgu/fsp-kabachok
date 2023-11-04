from enum import Enum


class AlarmistRoutes(Enum):
    USER = "/api/users/"
    DB = "/api/db/"
    HEALTHCHECK = "/api/healthcheck/"
    STATE = "/api/state"
