import threading
from datetime import datetime
import json
import subprocess


def _add_message_to_queue(message):
    # Define the message data and convert it to JSON
    message_json = json.dumps({
        "role": "computer",
        "type": "console",
        "format": "output",
        "content": message
    })
    subprocess.run(['logger', '{TO_INTERPRETER{' + message_json + '}TO_INTERPRETER}'])


def schedule(dt: datetime, message: str) -> None:
    """"Schedules a reminder at a specific time. At the specified time, the message will be added to the queue."""
    # Calculate the delay in seconds
    delay = (dt - datetime.now()).total_seconds()

    # Create a timer
    timer = threading.Timer(delay, _add_message_to_queue, args=[message])

    # Start the timer
    timer.start()