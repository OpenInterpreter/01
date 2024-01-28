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




def main(interpreter: OpenInterpreter):
    app = FastAPI()

    @app.websocket("/")
    async def i_test(websocket: WebSocket):
        await websocket.accept()
        data = None
        
        while True:
            # This is the task for waiting for the user to send any message at all.
            try:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            except:
                pass
            task = asyncio.create_task(websocket.receive_text())

            if data == None: # Data will have stuff in it if we inturrupted it.
                while data == None:
                    # Has the user sent a message?
                    if task.done():
                        try:
                            data = {"role": "user", "type": "message", "content": task.result()}
                        except Exception as e:
                            print(e)
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

                    # Has the queue recieved a message?
                    queued_message = check_queue()
                    if queued_message:
                        data = queued_message

                    await asyncio.sleep(0.2)
            
            ### CONVERSATION / DISC MANAGEMENT
            message = data
            messages = load_conversation()
            messages.append(message)
            save_conversation(messages)

            ### RESPONDING

            # This is the task for waiting for user inturruptions.
            try:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            except:
                pass
            task = asyncio.create_task(websocket.receive_text())

            recieved_chunks = []

            for chunk in interpreter.chat(
                messages, stream=True, display=True
            ):
                
                recieved_chunks.append(chunk)
                
                # Has the user sent a message?
                if task.done():
                    try:
                        data = {"role": "user", "type": "message", "content": task.result()}
                    except Exception as e:
                        print(e)
                    task.cancel() # The user didn't inturrupt
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    save_conversation(interpreter.messages)
                    break

                # Has the queue recieved a message?
                queued_message = check_queue()
                if queued_message:
                    data = queued_message
                    save_conversation(interpreter.messages)
                    break
                
                # Send out chunks
                await websocket.send_json(chunk)
                await asyncio.sleep(0.01)  # Add a small delay

                # If the interpreter just finished sending a message, save it
                if "end" in chunk:
                    save_conversation(interpreter.messages)
                    data = None

            if not any([message["type"] == "code" for message in recieved_chunks]):
                for chunk in interpreter.chat(
                    "Did you need to run code? It's okay if not, but please do if you did.", stream=True, display=True
                ):
                    # Has the user sent a message?
                    if task.done():
                        try:
                            data = {"role": "user", "type": "message", "content": task.result()}
                        except Exception as e:
                            print(e)
                        task.cancel() # The user didn't inturrupt
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                        save_conversation(interpreter.messages)
                        break

                    # Has the queue recieved a message?
                    queued_message = check_queue()
                    if queued_message:
                        data = queued_message
                        save_conversation(interpreter.messages)
                        break
                    
                    # Send out chunks
                    await websocket.send_json(chunk)
                    await asyncio.sleep(0.01)  # Add a small delay

                    # If the interpreter just finished sending a message, save it
                    if "end" in chunk:
                        save_conversation(interpreter.messages)
                        data = None

            if not task.done():
                task.cancel() # User didn't inturrupt
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            
        


    uvicorn.run(app, host="0.0.0.0", port=8000)