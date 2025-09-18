FROM python:3.10.0

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install -e .  # Installs dependencies using uv

ARG DEV=false
RUN uv sync

COPY ./app/ ./

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--env-file", ".env.prod", "--workers", "2", "--timeout-keep-alive", "900"]