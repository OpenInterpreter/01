### Import config from .env
if [ ! -f ".env" ]; then
    echo "Error: .env file does not exist. To create one, see .env.example for an example."
    exit 1
fi
set -a; source .env; set +a

### SETUP

# (for dev, reset the ports we were using)

SERVER_PORT=$(echo $SERVER_URL | grep -oE "[0-9]+")
if [ -n "$SERVER_PORT" ]; then
    lsof -ti tcp:$SERVER_PORT | xargs kill
fi

### START

start_device() {
    echo "Starting device..."
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

# DEVICE
# Start device if DEVICE_START is True
if [[ "$DEVICE_START" == "True" ]]; then
    start_device
fi

# SERVER
# Start server if SERVER_START is True
if [[ "$SERVER_START" == "True" ]]; then
    start_server
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