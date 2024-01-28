### Install Chromium if not already installed
if ! command -v chromium-browser &> /dev/null
then
    apt-get install chromium-browser
fi

### APP

# Dynamically get path to chrome executable and use it here
CHROME_PATH=$(which chromium-browser)
$CHROME_PATH --kiosk ----app=file:///app/index.html

### Start whisper.cpp and stuff?

### CORE

cd core/
poetry install
poetry run bash start.sh
