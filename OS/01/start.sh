### APP

# Display app/index.html on the second monitor in full-screen mode
google-chrome --kiosk --app=file:///app/index.html


### CORE

cd /core
poetry install
poetry run bash start.sh