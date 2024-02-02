import threading
from datetime import datetime
import json
import time
import redis

# Connect to Redis
r = redis.Redis()

def add_message_to_queue(message):

    # Define the message data and convert it to JSON
    message_json = json.dumps({
        "role": "computer",
        "type": "console",
        "format": "output",
        "content": message
    })

    # Add the message to the 'to_main' queue
    r.rpush('to_main', message_json)

def schedule(dt, message):
    # Calculate the delay in seconds
    delay = (dt - datetime.now()).total_seconds()

    # Create a timer
    timer = threading.Timer(delay, add_message_to_queue, args=[message])

    # Start the timer
    timer.start()