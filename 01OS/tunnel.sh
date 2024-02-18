#!/usr/bin/env bash

echo "Starting up localhost.run tunnel..."
ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run 2>&1 | while IFS= read -r line; do
    if [[ "$line" =~ https://([a-zA-Z0-9]+\.lhr\.life) ]]; then
        echo "Your free localhost.run tunnel is now active. Please set your client SERVER_CONNECTION_URL env var to: \"wss://${BASH_REMATCH[1]}\""
    fi
done
