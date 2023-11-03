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


class SharedResources(JSONSettings):
    pg_creds: DatabaseCredentials
