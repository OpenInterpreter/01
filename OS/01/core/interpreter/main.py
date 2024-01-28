"""
Responsible for taking an interpreter, then serving it at "/" as a websocket, accepting and streaming LMC Messages.

https://docs.openinterpreter.com/protocols/lmc-messages

Also needs to be saving conversations, and checking the queue.
"""

from typing import Optional, Tuple
import uvicorn
from fastapi import FastAPI, WebSocket
import asyncio
import json
import os
import glob
from interpreter.core.core import OpenInterpreter

def check_queue() -> dict:
    queue_files = glob.glob("interpreter/queue/*.json")
    if queue_files:
        with open(queue_files[0], 'r') as file:
            data = json.load(file)
        os.remove(queue_files[0])
        return data
    
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


def check_for_new_messages(task) -> Tuple[Optional[str], Optional[str]]:
    # Has the user sent a message?
    if task.done():
        return {"role": "user", "type": "message", "content": task.result()}

    # Has the queue recieved a message?
    queued_message = check_queue()
    if queued_message:
        return queued_message

    return None


async def get_new_messages(task) -> Tuple[Optional[str], Optional[str]]:
    message = check_for_new_messages(task)
    if message:
        return message
    else:
        await asyncio.sleep(0.2)
        return await get_new_messages(task)                  


def main(interpreter: OpenInterpreter):
    app = FastAPI()

    @app.websocket("/")
    async def i_test(websocket: WebSocket):
        await websocket.accept()
        data = None
        
        while True:
            # This is the task for waiting for the user to send any message at all.
            task = asyncio.create_task(websocket.receive_text())

            if data == None: # Data will have stuff in it if we inturrupted it.
                data = await get_new_messages(task)
            
            ### CONVERSATION / DISC MANAGEMENT
            message = data
            messages = load_conversation()
            messages.append(message)
            save_conversation(messages)

            ### RESPONDING

            # This is the task for waiting for user inturruptions.
            task = asyncio.create_task(websocket.receive_text())

            for chunk in interpreter.chat(
                messages, stream=True, display=True
            ):
                data = check_for_new_messages(task)
                if data:
                    save_conversation(interpreter.messages)
                    break
                
                # Send out chunks
                await websocket.send_json(chunk)
                await asyncio.sleep(0.01)  # Add a small delay

                # If the interpreter just finished sending a message, save it
                if "end" in chunk:
                    save_conversation(interpreter.messages)
                    data = None

            if data == None:
                task.cancel() # The user didn't inturrupt
        


    uvicorn.run(app, host="0.0.0.0", port=8000)