import time
import redis

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

def get_dmesg(after):
    """
    Is this the way to do this?
    """
    messages = []
    with open('/var/log/dmesg', 'r') as file:
        lines = file.readlines()
        for line in lines:
            timestamp = float(line.split(' ')[0].strip('[]'))
            if timestamp > after:
                messages.append(line)
    return messages

def custom_filter(message):
    # Check for {TO_INTERPRETER{ message here }TO_INTERPRETER} pattern
    if '{TO_INTERPRETER{' in message and '}TO_INTERPRETER}' in message:
        start = message.find('{TO_INTERPRETER{') + len('{TO_INTERPRETER{')
        end = message.find('}TO_INTERPRETER}', start)
        return message[start:end]
    # Check for USB mention
    elif 'USB' in message:
        return message
    # Check for network related keywords
    elif any(keyword in message for keyword in ['network', 'IP', 'internet', 'LAN', 'WAN', 'router', 'switch']):
        return message
    else:
        return None

last_timestamp = time.time()

while True:
    messages = get_dmesg(after=last_timestamp)
    last_timestamp = time.time()
    
    messages_for_core = []
    for message in messages:
        if custom_filter(message):
            messages_for_core.append(message)
    if messages_for_core != []:
        r.rpush('to_core', "\n".join(messages_for_core))

    time.sleep(5)