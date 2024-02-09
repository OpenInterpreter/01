### SETTINGS

# If ALL_LOCAL is False, we'll use OpenAI's services
export ALL_LOCAL=False
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
DEVICE_PORT=$(echo $DEVICE_URL | grep -oE "[0-9]+")
if [ -n "$DEVICE_PORT" ]; then
    lsof -ti tcp:$DEVICE_PORT | xargs kill
fi

# Check the current Python version
PYTHON_VERSION=$(python -V 2>&1 | cut -d " " -f 2 | cut -d "." -f 1-2)

# If the Python version is not 3.10 or 3.11, switch to it using pyenv
if [[ "$PYTHON_VERSION" != "3.10" ]] && [[ "$PYTHON_VERSION" != "3.11" ]]; then
    echo "Switching to Python 3.10 using pyenv..."
    pyenv install 3.10.0
    pyenv shell 3.10.0
fi

# INSTALL REQUIREMENTS

# (for dev, this is disabled for speed)

# if [[ "$OSTYPE" == "darwin"* ]]; then
#     brew update
#     brew install portaudio ffmpeg
# fi
# python -m pip install -r requirements.txt

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