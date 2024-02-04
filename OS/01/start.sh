### SETTINGS

export MODE_01=LIGHT
export ASSISTANT_PORT=8000
export COMPUTER_PORT=8001

# Kill whatever's on the ASSISTANT_PORT and COMPUTER_PORT
lsof -ti tcp:$ASSISTANT_PORT | xargs kill
lsof -ti tcp:$COMPUTER_PORT | xargs kill

### SETUP

# INSTALL REQUIREMENTS

# if [[ "$OSTYPE" == "darwin"* ]]; then
#     brew update
#     brew install portaudio ffmpeg
# fi
# pip install -r requirements.txt

### COMPUTER

# START KERNEL WATCHER

python computer/kernel_watcher.py &

# START RUN ENDPOINT

python computer/run.py &

# START SST AND TTS SERVICES

# (todo)
# (i think we should start with hosted services)

# START LLM

# (disabled, we'll start with hosted services)
# python core/llm/start.py &

sleep 6

# START ASSISTANT

python assistant/assistant.py &

### USER

# START USER

python user/user.py &