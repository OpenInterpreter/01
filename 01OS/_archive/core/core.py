import redis
import json
import time

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

def main(interpreter):

    while True:

        # Check 10x a second for new messages
        message = None
        while message is None:
            message = r.lpop('to_core')
            time.sleep(0.1)

        # Custom stop message will halt us
        if message.get("content") and message.get("content").lower().strip(".,!") == "stop":
            continue

        # Load, append, and save conversation history
        with open("conversations/user.json", "r") as file:
            messages = json.load(file)
        messages.append(message)
        with open("conversations/user.json", "w") as file:
            json.dump(messages, file)
        
        for chunk in interpreter.chat(messages):

            # Send it to the interface
            r.rpush('to_interface', chunk)
            
            # If we have a new message, save our progress and go back to the top
            if r.llen('to_main') > 0:
                with open("conversations/user.json", "w") as file:
                    json.dump(interpreter.messages, file)
                break
