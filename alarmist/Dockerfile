FROM kabachok:latest

COPY src src
ENTRYPOINT ["uvicorn", "--app-dir", "src", "--host", "0.0.0.0", "main:app"]
