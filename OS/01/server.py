from starlette.websockets import WebSocketDisconnect
import ast
import json
import time
import queue
import os
from queue import Queue
from threading import Thread
import uvicorn
import re
from fastapi import FastAPI
from threading import Thread
from starlette.websockets import WebSocket
from stt import stt
from tts import tts
from pathlib import Path
import asyncio
from i import configure_interpreter
import urllib.parse
from interpreter import interpreter

app = FastAPI()

conversation_history_path = Path(__file__).parent / 'conversations' / 'user.json'

# This is so we only say() full sentences
def is_full_sentence(text):
    return text.endswith(('.', '!', '?'))

def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

# Global queues
receive_queue = queue.Queue()
send_queue = queue.Queue()
recieve_computer_queue = queue.Queue() # Just for computer messages from the device

# Switch code executor to device if that's set

if os.getenv('CODE_RUNNER') == "device":

    # (This should probably just loop through all languages and apply these changes instead)

    class Python:
        # This is the name that will appear to the LLM.
        name = "python"

        def __init__(self):
            self.halt = False

        def run(self, code):
            """Generator that yields a dictionary in LMC Format."""

            # Prepare the data
            message = {"role": "assistant", "type": "code", "format": "python", "content": code}

            # Unless it was just sent to the device, send it wrapped in flags
            if not (interpreter.messages and interpreter.messages[-1] == message):
                send_queue.put({"role": "assistant", "type": "code", "format": "python", "start": True})
                send_queue.put(message)
                send_queue.put({"role": "assistant", "type": "code", "format": "python", "end": True})
            
            # Stream the response
            print("Waiting for the device to respond...")
            while True:
                chunk = recieve_computer_queue.get()
                print("Server recieved from device:", chunk)
                if "end" in chunk:
                    break
                yield chunk

        def stop(self):
            self.halt = True

        def terminate(self):
            """Terminates the entire process."""
            # dramatic!! do nothing
            pass

    interpreter.computer.languages = [Python]

# Configure interpreter
interpreter = configure_interpreter(interpreter)

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    receive_task = asyncio.create_task(receive_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket))
    await asyncio.gather(receive_task, send_task)

async def receive_messages(websocket: WebSocket):
    while True:
        data = await websocket.receive_text()
        if type(data) == dict and data["role"] == "computer":
            recieve_computer_queue.put(data) # To be handled by interpreter.computer.run
        else:
            receive_queue.put(data)

async def send_messages(websocket: WebSocket):
    while True:
        message = await asyncio.get_event_loop().run_in_executor(None, send_queue.get)
        print(message)
        await websocket.send_json(message)

def queue_listener():
    audio_file = bytearray()
    while True:
        # Check 10x a second for new messages
        while receive_queue.empty():
            time.sleep(0.1)
        message = receive_queue.get()

        message = json.loads(message)

        # Hold the audio in a buffer. If it's ready (we got end flag, stt it)
        if message["type"] == "audio":
            if "content" in message:
                audio_file.extend(bytes(ast.literal_eval(message["content"])))
            if "end" in message:
                content = stt(audio_file, message["format"])
                if content == None: # If it was nothing / silence
                    continue
                audio_file = bytearray()
                message = {"role": "user", "type": "message", "content": content}
            else:
                continue

        # Custom stop message will halt us
        if message.get("content") and message.get("content").lower().strip(".,!") == "stop":
            continue

        # Load, append, and save conversation history
        with open(conversation_history_path, 'r') as file:
            messages = json.load(file)
        messages.append(message)
        with open(conversation_history_path, 'w') as file:
            json.dump(messages, file)

        accumulated_text = ""
        
        for chunk in interpreter.chat(messages, stream=True):

            # Send it to the user
            send_queue.put(chunk)
            
            # Speak full sentences out loud
            if chunk["role"] == "assistant" and "content" in chunk:
                print("Chunk role is assistant and content is present in chunk.")
                accumulated_text += chunk["content"]
                print("Accumulated text: ", accumulated_text)
                sentences = split_into_sentences(accumulated_text)
                print("Sentences after splitting: ", sentences)
                if is_full_sentence(sentences[-1]):
                    print("Last sentence is a full sentence.")
                    for sentence in sentences:
                        print("Streaming sentence: ", sentence)
                        stream_tts_to_user(sentence)
                    accumulated_text = ""
                    print("Reset accumulated text.")
                else:
                    print("Last sentence is not a full sentence.")
                    for sentence in sentences[:-1]:
                        print("Streaming sentence: ", sentence)
                        stream_tts_to_user(sentence)
                    accumulated_text = sentences[-1]
                    print("Accumulated text is now the last sentence: ", accumulated_text)
            
            # If we have a new message, save our progress and go back to the top
            if not receive_queue.empty():
                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file)
                break

def stream_tts_to_user(sentence):
    send_queue.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "start": True})
    audio_bytes = tts(sentence)
    send_queue.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "content": str(audio_bytes)})
    send_queue.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "end": True})

# Create a thread for the queue listener
queue_thread = Thread(target=queue_listener)

# Start the queue listener thread
queue_thread.start()

# Run the FastAPI app
if __name__ == "__main__":
    server_url = os.getenv('SERVER_URL')
    if not server_url:
        raise ValueError("The environment variable SERVER_URL is not set. Please set it to proceed.")
    parsed_url = urllib.parse.urlparse(server_url)
    print("Starting `server.py`...")
    uvicorn.run(app, host=parsed_url.hostname, port=parsed_url.port)
