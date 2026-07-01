FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

RUN python -m pip install --no-cache-dir uv==0.11.24

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
