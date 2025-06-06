FROM n8nio/n8n:latest

USER root

# Install Docker CLI using Alpine's community repository
RUN apk update && \
    apk add --no-cache docker-cli && \
    rm -rf /var/cache/apk/*

USER node 