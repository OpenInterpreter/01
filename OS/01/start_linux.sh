### SETUP

# INSTALL REQUIREMENTS

sudo apt-get update
sudo apt-get install redis-server
pip install -r requirements.txt

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

# START ASSISTANT

python assistant/assistant.py &

### USER

# START USER

python user/user.py &