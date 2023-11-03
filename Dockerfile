FROM python:3.11 AS builder

ENV PIP_DEFAULT_TIMEOUT=200 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 

ENV RYE_HOME="/opt/rye"
ENV PATH="$RYE_HOME/shims:$PATH"
ENV WD_NAME=/app
WORKDIR $WD_NAME
RUN curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" RYE_NO_AUTO_INSTALL=1 bash

COPY pyproject.toml requirements*.lock .python-version README.md ./

RUN rye sync --no-lock --no-dev

ENV PACKAGE_PATH="/app/.venv/lib/python3.11/site-packages"
ENV PATH="/app/.venv/bin:$PATH"

COPY src src

FROM python:3.11-slim as runtime

ENV WD_NAME=/app
WORKDIR $WD_NAME

ENV PATH="$WD_NAME/.venv/bin:$PATH"
ENV PYTHONPATH="$PYTHONPATH:$WD_NAME/.venv/lib/python3.11/site-packages"

COPY --from=builder /opt/rye /opt/rye
COPY --from=builder $WD_NAME/.venv .venv
ENTRYPOINT ["python3", "src/main.py"]
