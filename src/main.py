import logging

from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger("app")


@app.get("/")
async def hello():
    return {"message": "Supervisor API is running"}
