from starlette.websockets import WebSocketDisconnect
import ast
import json
import time
import queue
import os
import traceback
from queue import Queue
from threading import Thread
import threading
import uvicorn
import re
from fastapi import FastAPI
from threading import Thread
from starlette.websockets import WebSocket
from stt import stt_bytes
from tts import tts
from pathlib import Path
import asyncio
import urllib.parse
from utils.kernel import put_kernel_messages_into_queue
from i import configure_interpreter
from interpreter import interpreter

app = FastAPI()

conversation_history_path = Path(__file__).parent / 'conversations' / 'user.json'

# This is so we only say() full sentences
def is_full_sentence(text):
    return text.endswith(('.', '!', '?'))

def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

# Queues
from_computer = queue.Queue() # Just for computer messages from the device. Sync queue because interpreter.run is synchronous
from_user = asyncio.Queue() # Just for user messages from the device.
to_device = asyncio.Queue() # For messages we send.

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
                to_device.put({"role": "assistant", "type": "code", "format": "python", "start": True})
                to_device.put(message)
                to_device.put({"role": "assistant", "type": "code", "format": "python", "end": True})
            
            # Stream the response
            print("Waiting for the device to respond...")
            while True:
                chunk = from_computer.get()
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
    try:
        await asyncio.gather(receive_task, send_task)
    except Exception as e:
        traceback.print_exc()
        print(f"Connection lost. Error: {e}")

async def receive_messages(websocket: WebSocket):
    while True:
        data = await websocket.receive_json()
        if data["role"] == "computer":
            from_computer.put(data) # To be handled by interpreter.computer.run
        elif data["role"] == "user":
            await from_user.put(data)
        else:
            raise("Unknown role:", data)

async def send_messages(websocket: WebSocket):
    while True:
        message = await to_device.get()
        print("Sending to the device:", type(message), message)
        await websocket.send_json(message)

async def listener():
    audio_bytes = bytearray()
    while True:
        while True:
            if not from_user.empty():
                message = await from_user.get()
                break
            elif not from_computer.empty():
                message = from_computer.get()
                break
            await asyncio.sleep(1)

        if type(message) == str:
            message = json.loads(message)

        # Hold the audio in a buffer. If it's ready (we got end flag, stt it)
        if message["type"] == "audio":
            if "content" in message:
                audio_bytes.extend(bytes(ast.literal_eval(message["content"])))
            if "end" in message:
                content = stt_bytes(audio_bytes, message["format"])
                if content == None: # If it was nothing / silence
                    continue
                audio_bytes = bytearray()
                message = {"role": "user", "type": "message", "content": content}
            else:
                continue

        # Ignore flags, we only needed them for audio ^
        if "content" not in message or message["content"] == None:
            continue

        # Custom stop message will halt us
        if message["content"].lower().strip(".,!") == "stop":
            continue

        # Load, append, and save conversation history
        with open(conversation_history_path, 'r') as file:
            messages = json.load(file)
        messages.append(message)
        with open(conversation_history_path, 'w') as file:
            json.dump(messages, file)

        accumulated_text = ""
        
        for chunk in interpreter.chat(messages, stream=True, display=False):

            print("Got chunk:", chunk)

            # Send it to the user
            await to_device.put(chunk)
            # Yield to the event loop, so you actually send it out
            await asyncio.sleep(0.01)
            
            # Speak full sentences out loud
            if chunk["role"] == "assistant" and "content" in chunk:
                accumulated_text += chunk["content"]
                sentences = split_into_sentences(accumulated_text)
                if is_full_sentence(sentences[-1]):
                    for sentence in sentences:
                        await stream_or_play_tts(sentence)
                    accumulated_text = ""
                else:
                    for sentence in sentences[:-1]:
                        await stream_or_play_tts(sentence)
                    accumulated_text = sentences[-1]
            
            # If we have a new message, save our progress and go back to the top
            if not from_user.empty():

                # Check if it's just an end flag. We ignore those.
                temp_message = await from_user.get()
                
                if temp_message == {'role': 'user', 'type': 'message', 'end': True}:
                    # Yup. False alarm.
                    continue
                else:
                    # Whoops! Put that back
                    await from_user.put(temp_message)

                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file)

                print("New user message recieved. Breaking.")
                break

            # Also check if there's any new computer messages
            if not from_computer.empty():
                
                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file)

                print("New computer message recieved. Breaking.")
                break
            

async def stream_or_play_tts(sentence):

    if os.getenv('TTS_RUNNER') == "server":
        tts(sentence, play_audio=True)
    else:
        await to_device.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "start": True})
        audio_bytes = tts(sentence, play_audio=False)
        await to_device.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "content": str(audio_bytes)})
        await to_device.put({"role": "assistant", "type": "audio", "format": "audio/mp3", "end": True})


from uvicorn import Config, Server

# Run the FastAPI app
if __name__ == "__main__":

    async def main():
        # Start listening
        asyncio.create_task(listener())

        # Start watching the kernel if it's your job to do that
        if os.getenv('CODE_RUNNER') == "server":
            asyncio.create_task(put_kernel_messages_into_queue(from_computer))

        server_url = os.getenv('SERVER_URL')
        if not server_url:
            raise ValueError("The environment variable SERVER_URL is not set. Please set it to proceed.")
        parsed_url = urllib.parse.urlparse(server_url)
        print("Starting `server.py`...")

        config = Config(app, host=parsed_url.hostname, port=parsed_url.port, lifespan='on')
        server = Server(config)
        await server.serve()

    asyncio.run(main())