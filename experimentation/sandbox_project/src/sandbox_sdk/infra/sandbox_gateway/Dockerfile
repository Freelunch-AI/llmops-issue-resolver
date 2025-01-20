FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN curl -fsSL https://astral.sh/uv/install.sh | sh
RUN uv pip install --no-cache -r requirements.txt

COPY api/ api/

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]