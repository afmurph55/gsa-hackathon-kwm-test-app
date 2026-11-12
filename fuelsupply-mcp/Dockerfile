# Local stdio image; no deployment is authorized or tested.
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY config ./config
RUN uv sync --locked --no-dev --python /usr/local/bin/python
CMD ["/app/.venv/bin/fuelsupply-mcp"]
