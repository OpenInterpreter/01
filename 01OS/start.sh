#!/usr/bin/env bash

# Set python to prioritize the module files from the current directory
# If we don't do this, then the python interpreter will not be able to find the modules,
# and will throw an error like "ModuleNotFoundError: No module named '01OS'".
# If we solve the problem by pip installing the official 01OS package, then those
# modules will run instead of the local ones that we are trying to develop with.
export PYTHONPATH="$(pwd):$PYTHONPATH"

### Import Environment Variables from .env
SCRIPT_DIR="$(dirname "$0")"
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "No .env file found. Copying from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
fi
set -a; source "$SCRIPT_DIR/.env"; set +a

### COMMAND LINE ARGUMENTS

# Set both SERVER_START and CLIENT_START to False if "--server" or "--client" is passed as an argument
# (This way, --server runs only the server, --client runs only the client.)
if [[ "$@" == *"--server"* ]] || [[ "$@" == *"--client"* ]]; then
    export SERVER_START="False"
    export CLIENT_START="False"
fi

# Check if "--local" is passed as an argument
if [[ "$@" == *"--local"* ]]; then
    # If "--local" is passed, set ALL_LOCAL to True
    export ALL_LOCAL="True"
fi

# Check if "--server" is passed as an argument
if [[ "$@" == *"--server"* ]]; then
    # If "--server" is passed, set SERVER_START to True
    export SERVER_START="True"
fi

# Check if "--client" is passed as an argument
if [[ "$@" == *"--client"* ]]; then
    # If "--client" is passed, set CLIENT_START to True
    export CLIENT_START="True"
    # Extract the client type from the arguments
    CLIENT_TYPE=$(echo "$@" | sed -n -e 's/^.*--client //p' | awk '{print $1}')
    # If client type is not empty, export it
    if [[ ! -z "$CLIENT_TYPE" ]]; then
        export CLIENT_TYPE
    fi
fi

# Check if "--expose" is passed as an argument
if [[ "$@" == *"--expose"* ]]; then
    # If "--expose" is passed, set SERVER_EXPOSE_PUBLICALLY to True
    export SERVER_EXPOSE_PUBLICALLY="True"
fi

# Check if "--clear-local" is passed as an argument
if [[ "$@" == *"--clear-local"* ]]; then
    # If "--clear-local" is passed, clear the contents of the folders in script_dir/01OS/server/{tts and stt}/local_service
    echo "Clearing local services..."
    rm -rf "$SCRIPT_DIR/01OS/server/tts/local_service"/*
    rm -rf "$SCRIPT_DIR/01OS/server/stt/local_service"/*
    echo "Exiting after clearing local services..."
    exit 0
fi

### SETUP

if [[ "$ALL_LOCAL" == "True" ]]; then
    # if using local models, install the models / executables

    ## WHISPER
    
    WHISPER_MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"
    WHISPER_PATH="$SCRIPT_DIR/01OS/server/stt/local_service"
    if [[ ! -f "${WHISPER_PATH}/${WHISPER_MODEL_NAME}" ]]; then
        mkdir -p "${WHISPER_PATH}"
        curl -L "${WHISPER_MODEL_URL}${WHISPER_MODEL_NAME}" -o "${WHISPER_PATH}/${WHISPER_MODEL_NAME}"
    fi

    ## PIPER

    PIPER_FILE_PATH="$SCRIPT_DIR/01OS/server/tts/local_service${PIPER_URL}${PIPER_ASSETNAME}"
    if [[ ! -f "$PIPER_FILE_PATH" ]]; then   

        mkdir -p "${PIPER_FILE_PATH}"

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
        
        # Save the current working directory
        CWD=$(pwd)

        # Navigate to SCRIPT_DIR/01OS/server/tts/local_service
        cd $SCRIPT_DIR/01OS/server/tts/local_service

        curl -L "${PIPER_URL}${PIPER_ASSETNAME}" -o "${PIPER_ASSETNAME}"
        tar -xvzf $PIPER_ASSETNAME
        cd piper
        curl -OL "${PIPER_VOICE_URL}${PIPER_VOICE_NAME}"
        curl -OL "${PIPER_VOICE_URL}${PIPER_VOICE_NAME}.json"
        if [ "$OS" = "macos" ]; then
            if [ "$ARCH" = "x64" ]; then
                softwareupdate --install-rosetta --agree-to-license
            fi
            PIPER_PHONEMIZE_ASSETNAME="piper-phonemize_${OS}_${ARCH}.tar.gz"
            PIPER_PHONEMIZE_URL="https://github.com/rhasspy/piper-phonemize/releases/latest/download/"
            curl -OL "${PIPER_PHONEMIZE_URL}${PIPER_PHONEMIZE_ASSETNAME}"
            tar -xvzf $PIPER_PHONEMIZE_ASSETNAME
            PIPER_DIR=`pwd`
            install_name_tool -change @rpath/libespeak-ng.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libespeak-ng.1.dylib" "${PIPER_DIR}/piper"
            install_name_tool -change @rpath/libonnxruntime.1.14.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libonnxruntime.1.14.1.dylib" "${PIPER_DIR}/piper"
            install_name_tool -change @rpath/libpiper_phonemize.1.dylib "${PIPER_DIR}/piper-phonemize/lib/libpiper_phonemize.1.dylib" "${PIPER_DIR}/piper"
        fi

        # Navigate back to the current working directory
        cd $CWD
    fi
fi

### START

start_client() {
    echo "Starting client..."
    bash $SCRIPT_DIR/01OS/clients/start.sh &
    CLIENT_PID=$!
    echo "client started as process $CLIENT_PID"
}

# Function to start server
start_server() {
    echo "Starting server..."
    python -m 01OS.server.server &
    SERVER_PID=$!
    echo "Server started as process $SERVER_PID"
}

stop_processes() {
    if [[ -n $CLIENT_PID ]]; then
        echo "Stopping client..."
        kill $CLIENT_PID
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

# CLIENT
# Start client if CLIENT_START is True
if [[ "$CLIENT_START" == "True" ]]; then
    start_client
fi

# Wait for client and server processes to exit
wait $CLIENT_PID
wait $SERVER_PID

# TTS, STT

# (todo)
# (i think we should start with hosted services)

# LLM

# (disabled, we'll start with hosted services)
# python core/llm/start.py &