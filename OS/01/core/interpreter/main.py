"""
Responsible for taking an interpreter, then serving it at "/" as a websocket, accepting and streaming LMC Messages.

https://docs.openinterpreter.com/protocols/lmc-messages

Also needs to be saving conversations, and checking the queue.
"""

import uvicorn
from fastapi import FastAPI, WebSocket
import asyncio
import json
import os
import glob

def check_queue():
    queue_files = glob.glob("interpreter/queue/*.json")
    if queue_files:
        with open(queue_files[0], 'r') as file:
            data = json.load(file)
        os.remove(queue_files[0])
        return data
    else:
        return None
    
def save_conversation(messages):
    with open('interpreter/conversations/user.json', 'w') as file:
        json.dump(messages, file)

def load_conversation():
    try:
        with open('interpreter/conversations/user.json', 'r') as file:
            messages = json.load(file)
        return messages
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def main(interpreter):

    app = FastAPI()

    @app.websocket("/")
    async def i_test(websocket: WebSocket):
        await websocket.accept()
        data = None
        
        while True:
            # This is the task for waiting for the user to send any message at all.
            task = asyncio.create_task(websocket.receive_text())

            if data == None: # Data will have stuff in it if we inturrupted it.
                while True:
                    # Has the user sent a message?
                    if task.done():
                        data = task.result()
                        break

                    # Has the queue recieved a message?
                    queued_message = check_queue()
                    if queued_message:
                        data = queued_message
                        break
                    
                    # Wait 0.2 seconds
                    await asyncio.sleep(0.2)

            ### FOR DEV ONLY: SIMULATE LMC MESSAGES
            # This lets users simulate any kind of LMC message by passing a JSON into the textbox in index.html.

            try:
                data_dict = json.loads(data)
                data = data_dict
            except json.JSONDecodeError:
                pass
            
            ### CONVERSATION / DISC MANAGEMENT
            user_message = {"role": "user", "type": "message", "content": data}
            messages = load_conversation()
            messages.append(user_message)
            save_conversation(messages)

            ### RESPONDING

            # This is the task for waiting for user inturruptions.
            task = asyncio.create_task(websocket.receive_text())

            for chunk in interpreter.chat(
                messages, stream=True, display=True
            ):
                print(chunk)
                # Check queue
                queued_message = check_queue()
                if queued_message:
                    data = queued_message
                    break

                # Check for new user messages
                if task.done():
                    data = task.result()  # Get the new message
                    break  # Break the loop and start processing the new message
                
                # Send out chunks
                await websocket.send_json(chunk)
                await asyncio.sleep(0.01)  # Add a small delay

                # If the interpreter just finished sending a message, save it
                if "end" in chunk:
                    save_conversation(interpreter.messages)
                    data = None
        


    uvicorn.run(app, host="0.0.0.0", port=8000)