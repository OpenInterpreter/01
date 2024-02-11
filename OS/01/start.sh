### SETTINGS

# If ALL_LOCAL is False, we'll use OpenAI's services
# else we use whisper.cpp and piper local models
export ALL_LOCAL=False
export WHISPER_MODEL_NAME="ggml-tiny.en.bin"

# Uncomment and set the OpenAI API key for OpenInterpreter to work
# export OPENAI_API_KEY="sk-..."

# Expose through Ngrok
# Uncomment following line with your Ngrok auth token (https://dashboard.ngrok.com/get-started/your-authtoken)
# export NGROK_AUTHTOKEN="AUTH_TOKEN"

# For TTS, we use the en_US-lessac-medium voice model by default
# Please change the voice URL and voice name if you wish to use another voice
export PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/"
export PIPER_VOICE_NAME="en_US-lessac-medium.onnx"

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
# export LOG_LEVEL=DEBUG
export LOG_LEVEL="INFO"


### SETUP

# if using local models, install the models / executables
WHISPER_MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"
WHISPER_RUST_PATH="`pwd`/local_stt/whisper-rust"

curl -OL "${WHISPER_MODEL_URL}${WHISPER_MODEL_NAME}" --output-dir ${WHISPER_RUST_PATH}

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