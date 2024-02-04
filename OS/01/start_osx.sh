### SETUP

# INSTALL REQUIREMENTS

brew update
brew install portaudio ffmpeg
pip install -r requirements.txt

### CORE

# START KERNEL WATCHER

python core/kernel_watcher.py &

# START SST AND TTS SERVICES

# (todo)
# (i think we should start with hosted services)

# START LLM

# (disabled, we'll start with hosted services)
# python core/llm/start.py &

# START CORE

python core/start_core.py &


### INTERFACE

# START INTERFACE

python interface/interface.py &

# START DISPLAY

# (this should be changed to run it in fullscreen / kiosk mode)
open interface/display.html