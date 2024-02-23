#!/usr/bin/env bash

# Get tunnel method from TUNNEL_METHOD environment variable, but default to bore
# Possible options;
# - bore
# - localtunnel
# - ngrok
TUNNEL_METHOD=${TUNNEL_METHOD:-bore}

# Get the SERVER_PORT environment variable, but default to 8000
SERVER_LOCAL_PORT=${SERVER_LOCAL_PORT:-8000}

echo "Using $TUNNEL_METHOD to expose port $SERVER_LOCAL_PORT on localhost..."

# If the TUNNEL_METHOD is bore, then we need to check if the bore-cli is installed
if [[ "$TUNNEL_METHOD" == "bore" ]]; then

    if ! command -v bore &> /dev/null; then
        echo "The bore-cli command is not available. Please run 'cargo install bore-cli'."
        echo "For more information, see https://github.com/ekzhang/bore"
        exit 1
    else
        bore local $SERVER_LOCAL_PORT --to bore.pub | while IFS= read -r line; do
            if [[ "$line" == *"listening at bore.pub:"* ]]; then
                remote_port=$(echo "$line" | grep -o 'bore.pub:[0-9]*' | cut -d':' -f2)
                echo "Please set your client env variable for SERVER_URL=ws://bore.pub:$remote_port"
                break
            fi
        done
    fi

elif [[ "$TUNNEL_METHOD" == "localtunnel" ]]; then

    if ! command -v lt &> /dev/null; then
        echo "The 'lt' command is not available."
        echo "Please ensure you have Node.js installed, then run 'npm install -g localtunnel'."
        echo "For more information, see https://github.com/localtunnel/localtunnel"
        exit 1
    else
        npx localtunnel --port $SERVER_LOCAL_PORT | while IFS= read -r line; do
            if [[ "$line" == *"your url is: https://"* ]]; then
                remote_url=$(echo "$line" | grep -o 'https://[a-zA-Z0-9.-]*' | sed 's|https://||')
                echo "Please set your client env variable for SERVER_URL=wss://$remote_url"
                break
            fi
        done
    fi

elif [[ "$TUNNEL_METHOD" == "ngrok" ]]; then

    if ! command -v ngrok &> /dev/null; then
        echo "The ngrok command is not available."
        echo "Please install ngrok using the instructions at https://ngrok.com/docs/getting-started/"
        exit 1
    else
        ngrok http $SERVER_LOCAL_PORT --log stdout | while IFS= read -r line; do
            if [[ "$line" == *"started tunnel"* ]]; then
                remote_url=$(echo "$line" | grep -o 'https://[a-zA-Z0-9.-]*' | sed 's|https://||')
                echo "Please set your client env variable for SERVER_URL=wss://$remote_url"
                break
            fi
        done
    fi

fi
