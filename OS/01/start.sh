### SETTINGS

# If ALL_LOCAL is False, we'll use OpenAI's services
# If setting ALL_LOCAL to true, set the path to the WHISPER local model
export ALL_LOCAL=False
# export WHISPER_MODEL_PATH=...
# export OPENAI_API_KEY=sk-...

# If SERVER_START, this is where we'll serve the server.
# If DEVICE_START, this is where the device expects the server to be.
export SERVER_URL=ws://localhost:8000/
export SERVER_START=True
export DEVICE_START=True

# Control where various operations happen— can be `device` or `server`.
export CODE_RUNNER=server
export TTS_RUNNER=server # If device, audio will be sent over websocket.
export STT_RUNNER=device # If server, audio will be sent over websocket.

# Will expose the server publically and display that URL.
export SERVER_EXPOSE_PUBLICALLY=False

### SETUP

# (for dev, reset the ports we were using)

SERVER_PORT=$(echo $SERVER_URL | grep -oE "[0-9]+")
if [ -n "$SERVER_PORT" ]; then
    lsof -ti tcp:$SERVER_PORT | xargs kill
fi

### START

# DEVICE

if [[ "$DEVICE_START" == "True" ]]; then
    python device.py &
fi

# SERVER

if [[ "$SERVER_START" == "True" ]]; then
    python server.py &
fi

# TTS, STT

# (todo)
# (i think we should start with hosted services)

# LLM

# (disabled, we'll start with hosted services)
# python core/llm/start.py &