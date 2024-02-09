import threading
from datetime import datetime
import json
import subprocess

def add_message_to_queue(message):

    # Define the message data and convert it to JSON
    message_json = json.dumps({
        "role": "computer",
        "type": "console",
        "format": "output",
        "content": message
    })
    subprocess.run(['logger', '{TO_INTERPRETER{' + message_json + '}TO_INTERPRETER}'])

def schedule(dt, message):
    # Calculate the delay in seconds
    delay = (dt - datetime.now()).total_seconds()

    # Create a timer
    timer = threading.Timer(delay, add_message_to_queue, args=[message])

    # Start the timer
    timer.start()