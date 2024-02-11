### SETTINGS

# If ALL_LOCAL is False, we'll use OpenAI's services
# If setting ALL_LOCAL to true, set the path to the WHISPER local model
export ALL_LOCAL=False
# export WHISPER_MODEL_PATH=...
export OPENAI_API_KEY="sk-..."

# Expose through Ngrok
# Uncomment following line with your Ngrok auth token (https://dashboard.ngrok.com/get-started/your-authtoken)
# export NGROK_AUTHTOKEN="AUTH_TOKEN"

# If SERVER_START, this is where we'll serve the server.
# If DEVICE_START, this is where the device expects the server to be.
export SERVER_URL=ws://localhost:8000/
export SERVER_CONNECTION_URL=$SERVER_URL # Comment if setting up through Ngrok
export SERVER_START=True
export DEVICE_START=True

# Control where various operations happen— can be `device` or `server`.
export CODE_RUNNER=server
export TTS_RUNNER=server # If device, audio will be sent over websocket.
export STT_RUNNER=device # If server, audio will be sent over websocket.

# Will expose the server publically and display that URL.
export SERVER_EXPOSE_PUBLICALLY=False

# Debug level
# export DEBUG_LEVEL=DEBUG
export DEBUG_LEVEL="INFO"


### SETUP

# (for dev, reset the ports we were using)

SERVER_PORT=$(echo $SERVER_URL | grep -oE "[0-9]+")
if [ -n "$SERVER_PORT" ]; then
    lsof -ti tcp:$SERVER_PORT | xargs kill
fi

### START

start_device() {
    echo "Starting device..."
    if [[ -n $NGROK_AUTHTOKEN ]]; then
        echo "Waiting for Ngrok to setup"
        sleep 7
        read -p "Enter the Ngrok URL: " ngrok_url
        export SERVER_CONNECTION_URL=$ngrok_url
        echo "SERVER_CONNECTION_URL set to $SERVER_CONNECTION_URL"
    fi

    python device.py &
    DEVICE_PID=$!
    echo "Device started as process $DEVICE_PID"
}

# Function to start server
start_server() {
    echo "Starting server..."
    python server.py &
    SERVER_PID=$!
    echo "Server started as process $SERVER_PID"
}

stop_processes() {
    if [[ -n $DEVICE_PID ]]; then
        echo "Stopping device..."
        kill $DEVICE_PID
    fi
    if [[ -n $SERVER_PID ]]; then
        echo "Stopping server..."
        kill $SERVER_PID
    fi
}

# Trap SIGINT and SIGTERM to stop processes when the script is terminated
trap stop_processes SIGINT SIGTERM

# SERVER
# Start server if SERVER_START is True
if [[ "$SERVER_START" == "True" ]]; then
    start_server
fi

# DEVICE
# Start device if DEVICE_START is True
if [[ "$DEVICE_START" == "True" ]]; then
    start_device
fi

# Wait for device and server processes to exit
wait $DEVICE_PID
wait $SERVER_PID

# TTS, STT

# (todo)
# (i think we should start with hosted services)

# LLM

# (disabled, we'll start with hosted services)
# python core/llm/start.py &