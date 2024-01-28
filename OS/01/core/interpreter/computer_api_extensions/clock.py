import threading
from datetime import datetime
import json
import time

class Clock:
    def __init__(self, computer):
        self.computer = computer

    def schedule(self, dt, message):
        # Calculate the delay in seconds
        delay = (dt - datetime.now()).total_seconds()

        # Create a timer
        timer = threading.Timer(delay, self.add_message_to_queue, args=[message])

        # Start the timer
        timer.start()

    def add_message_to_queue(self, message):

        # Define the message data and convert it to JSON
        message_json = json.dumps({
            "role": "computer",
            "type": "message",
            "content": message
        })

        # Write the JSON data to the file
        timestamp = str(int(time.time()))
        with open(f"/01/core/queue/{timestamp}.json", "w") as file:
            file.write(message_json)

