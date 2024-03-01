import threading
from datetime import datetime
import json
import subprocess
import requests


def send_request(message) -> None:
    url = "http://localhost:8000/"
    data = {"text": message}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")  

def schedule(days=0, hours=0, mins=0, secs=0, target_datetime=None, message="") -> None:
    """Schedules a reminder after a specified delay or for a specific datetime. The delay is defined by days, hours, minutes, and seconds. If a target_datetime is provided, it schedules the reminder for that datetime instead."""
    
    if target_datetime is None:
        # Calculate the delay in seconds if no target_datetime is provided
        delay = days * 86400 + hours * 3600 + mins * 60 + secs
    else:
        # Calculate the delay in seconds from now until the target datetime
        now = datetime.now()
        delay = (target_datetime - now).total_seconds()
        # Ensure delay is non-negative
        delay = max(0, delay)

    # Create a timer
    timer = threading.Timer(delay, send_request, args=[message])

    # Start the timer
    timer.start()                                                                     