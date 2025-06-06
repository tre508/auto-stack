FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set the port from environment or default to 5050
ARG CONTROLLER_PORT=5050
ENV PORT=$CONTROLLER_PORT

EXPOSE 5050

# Use shell form for CMD so $PORT is expanded at runtime
CMD uvicorn controller:app --host 0.0.0.0 --port $PORT 