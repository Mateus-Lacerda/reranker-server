FROM python:3.12-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.15 /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY model/pyproject.toml ./model/

RUN uv sync --locked

COPY model ./model

RUN . .venv/bin/activate && \
    cd model && \
    bash export_model.sh --full

FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.9.15 /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY model/pyproject.toml ./model/

RUN uv sync --locked --no-dev --no-install-project --package reranker-server

COPY --from=builder /app/model/onnx_full ./model/onnx_full

COPY src ./src
COPY __main__.py .

RUN uv sync --locked --no-dev --package reranker-server

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

ARG POOL_SIZE
ARG MODEL_PATH
ARG TOKENIZER_PATH
ARG SERVER_PORT
ARG RUN_SINGLE_THREADED

ENV POOL_SIZE=${POOL_SIZE:-"1"}
ENV MODEL_PATH=${MODEL_PATH:-"model/onnx_full/model.onnx"}
ENV TOKENIZER_PATH=${TOKENIZER_PATH:-"model/onnx_full/tokenizer.json"}
ENV SERVER_PORT=${SERVER_PORT:-"50051"}
ENV RUN_SINGLE_THREADED=${RUN_SINGLE_THREADED:-"true"}

EXPOSE 50051

CMD ["uv", "run", "."]
