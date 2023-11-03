from fastapi import FastAPI, Response, status
from fastapi.exceptions import HTTPException
import logging

app = FastAPI()
logger = logging.getLogger("app")


@app.get("/")
async def hello():
    return {"message": "Supervisor API is running"}
