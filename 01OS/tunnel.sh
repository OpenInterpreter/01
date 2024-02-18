#!/usr/bin/env bash

# Get the SERVER_PORT environment variable, but default to 8000
SERVER_LOCAL_PORT=${SERVER_LOCAL_PORT:-8000}

echo "Starting up localtunnel service for port $SERVER_LOCAL_PORT on localhost..."

npx localtunnel --port $SERVER_LOCAL_PORT | while IFS= read -r line; do
    if [[ "$line" == "your url is: https://"* ]]; then
        echo "Tunnel is up!"
        echo "Please set your client env variable for SERVER_CONNECTION_URL=wss://${line:21}"
        break
    fi
done
