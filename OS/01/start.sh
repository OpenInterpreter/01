### Import config from .env
if [ ! -f ".env" ]; then
    echo "Error: .env file does not exist. To create one, see .env.example for an example."
    exit 1
fi
set -a; source .env; set +a


### SETUP

# if using local models, install the models / executables
if [[ "$ALL_LOCAL" == "True" ]]; then
    OS=$(uname -s)
    ARCH=$(uname -m)
    if [ "$OS" = "Darwin" ]; then
        OS="macos"
        if [ "$ARCH" = "arm64" ]; then
            ARCH="aarch64"
        elif [ "$ARCH" = "x86_64" ]; then
            ARCH="x64"
        else
            echo "Piper: unsupported architecture"
        fi
    fi
    PIPER_ASSETNAME="piper_${OS}_${ARCH}.tar.gz"
    PIPER_URL="https://github.com/rhasspy/piper/releases/latest/download/"
    mkdir local_tts
    cd local_tts
    curl -OL "${PIPER_URL}${PIPER_ASSETNAME}"
    tar -xvzf $PIPER_ASSETNAME
    cd piper
    if [ "$OS" = "macos" ]; then
        if [ "$ARCH" = "x64" ]; then
            softwareupdate --install-rosetta --agree-to-license
        fi
        PIPER_PHONEMIZE_ASSETNAME="piper-phonemize_${OS}_${ARCH}.tar.gz"
        PIPER_PHONEMIZE_URL="https://github.com/rhasspy/piper-phonemize/releases/latest/download/"

        curl -OL "${PIPER_PHONEMIZE_URL}${PIPER_PHONEMIZE_ASSETNAME}"
        tar -xvzf $PIPER_PHONEMIZE_ASSETNAME
        curl -OL "${PIPER_VOICE_URL}${PIPER_VOICE_NAME}"
        curl -OL "${PIPER_VOICE_URL}${PIPER_VOICE_NAME}.json"
        PIPER_DIR=`pwd`
        install_name_tool -change @rpath/libespeak-ng.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libespeak-ng.1.dylib" "${PIPER_DIR}/piper"
        install_name_tool -change @rpath/libonnxruntime.1.14.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libonnxruntime.1.14.1.dylib" "${PIPER_DIR}/piper"
        install_name_tool -change @rpath/libpiper_phonemize.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libpiper_phonemize.1.dylib" "${PIPER_DIR}/piper"
    fi
    cd ../..
fi

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