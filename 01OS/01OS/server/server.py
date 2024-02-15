from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import ast
import json
import queue
import os
import traceback
import re
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from .stt.stt import stt_bytes
from .tts.tts import stream_tts
from pathlib import Path
import asyncio
import urllib.parse
from .utils.kernel import put_kernel_messages_into_queue
from .i import configure_interpreter
from interpreter import interpreter
import ngrok
from ..utils.accumulator import Accumulator

from .utils.logs import setup_logging
from .utils.logs import logger
setup_logging()

accumulator = Accumulator()

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
            logger.info("Waiting for the device to respond...")
            while True:
                chunk = from_computer.get()
                logger.info(f"Server received from device: {chunk}")
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

@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    receive_task = asyncio.create_task(receive_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket))
    try:
        await asyncio.gather(receive_task, send_task)
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.info(f"Connection lost. Error: {e}")

async def receive_messages(websocket: WebSocket):
    while True:
        try:
            try:
                data = await websocket.receive()
            except Exception as e:
                print(str(e))
                return
            if 'text' in data:
                try:
                    data = json.loads(data['text'])
                    if data["role"] == "computer":
                        from_computer.put(data) # To be handled by interpreter.computer.run
                    elif data["role"] == "user":
                        await from_user.put(data)
                    else:
                        raise("Unknown role:", data)
                except json.JSONDecodeError:
                    pass  # data is not JSON, leave it as is
            elif 'bytes' in data:
                data = data['bytes']  # binary data
                await from_user.put(data)
        except WebSocketDisconnect as e:
            if e.code == 1000:
                logger.info("Websocket connection closed normally.")
                return
            else:
                raise
        

async def send_messages(websocket: WebSocket):
    while True:
        message = await to_device.get()
        logger.debug(f"Sending to the device: {type(message)} {message}")
        
        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            elif isinstance(message, bytes):
                await websocket.send_bytes(message)
            else:
                raise TypeError("Message must be a dict or bytes")
        except:
            # Make sure to put the message back in the queue if you failed to send it
            await to_device.put(message)
            raise

async def listener():

    while True:
        while True:
            if not from_user.empty():
                chunk = await from_user.get()
                break
            elif not from_computer.empty():
                chunk = from_computer.get()
                break
            await asyncio.sleep(1)

        

        message = accumulator.accumulate(chunk)
        if message == None:
            # Will be None until we have a full message ready
            continue

        # print(str(message)[:1000])

        # At this point, we have our message

        if message["type"] == "audio" and message["format"].startswith("bytes"):

            if not message["content"]: # If it was nothing / silence
                continue

            # Convert bytes to audio file
            # Format will be bytes.wav or bytes.opus
            mime_type = "audio/" + message["format"].split(".")[1]
            text = stt_bytes(message["content"], mime_type)
            message = {"role": "user", "type": "message", "content": text}

        # At this point, we have only text messages

        # Custom stop message will halt us
        if message["content"].lower().strip(".,! ") == "stop":
            continue

        # Load, append, and save conversation history
        with open(conversation_history_path, 'r') as file:
            messages = json.load(file)
        messages.append(message)
        with open(conversation_history_path, 'w') as file:
            json.dump(messages, file, indent=4)

        accumulated_text = ""
        
        for chunk in interpreter.chat(messages, stream=True, display=False):

            logger.debug("Got chunk:", chunk)

            # Send it to the user
            await to_device.put(chunk)
            # Yield to the event loop, so you actually send it out
            await asyncio.sleep(0.01)
            
            if os.getenv('TTS_RUNNER') == "server":
                # Speak full sentences out loud
                if chunk["role"] == "assistant" and "content" in chunk:
                    accumulated_text += chunk["content"]
                    sentences = split_into_sentences(accumulated_text)
                    
                    # If we're going to speak, say we're going to stop sending text.
                    # This should be fixed probably, we should be able to do both in parallel, or only one.
                    if any(is_full_sentence(sentence) for sentence in sentences):
                        await to_device.put({"role": "assistant", "type": "message", "end": True})
                    
                    if is_full_sentence(sentences[-1]):
                        for sentence in sentences:
                            await stream_tts_to_device(sentence)
                        accumulated_text = ""
                    else:
                        for sentence in sentences[:-1]:
                            await stream_tts_to_device(sentence)
                        accumulated_text = sentences[-1]

                    # If we're going to speak, say we're going to stop sending text.
                    # This should be fixed probably, we should be able to do both in parallel, or only one.
                    if any(is_full_sentence(sentence) for sentence in sentences):
                        await to_device.put({"role": "assistant", "type": "message", "start": True})
                
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
                    json.dump(interpreter.messages, file, indent=4)

                logger.info("New user message recieved. Breaking.")
                break

            # Also check if there's any new computer messages
            if not from_computer.empty():
                
                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file, indent=4)

                logger.info("New computer message recieved. Breaking.")
                break
        else:
            with open(conversation_history_path, 'w') as file:
                json.dump(interpreter.messages, file, indent=4)  

async def stream_tts_to_device(sentence):
    for chunk in stream_tts(sentence):
        await to_device.put(chunk)
        
async def setup_ngrok(ngrok_auth_token, parsed_url):
    # Set up Ngrok
    logger.info("Setting up Ngrok")
    ngrok_listener = await ngrok.forward(f"{parsed_url.hostname}:{parsed_url.port}", authtoken=ngrok_auth_token)
    ngrok_parsed_url = urllib.parse.urlparse(ngrok_listener.url())

    # Setup SERVER_URL environment variable for device to use
    connection_url = f"wss://{ngrok_parsed_url.hostname}/"
    logger.info(f"Ngrok established at {ngrok_parsed_url.geturl()}")
    logger.info(f"\033[1mSERVER_CONNECTION_URL should be set to \"{connection_url}\"\033[0m")


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

        # Set up Ngrok
        ngrok_auth_token = os.getenv('NGROK_AUTHTOKEN')
        if ngrok_auth_token is not None:
            await setup_ngrok(ngrok_auth_token, parsed_url)
            
        logger.info("Starting `server.py`...")

        config = Config(app, host=parsed_url.hostname, port=parsed_url.port, lifespan='on')
        server = Server(config)
        await server.serve()

    asyncio.run(main())