FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG MEM0_API_PORT=8000
ENV PORT=$MEM0_API_PORT
EXPOSE 8000

CMD uvicorn app:app --host 0.0.0.0 --port $PORT 