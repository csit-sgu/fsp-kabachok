import logging

from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
async def hello():
    return {"message": "Semya is running"}
