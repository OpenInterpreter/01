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
from ..utils.accumulator import Accumulator
from .teach import teach
from .utils.logs import setup_logging
from .utils.logs import logger
setup_logging()

accumulator = Accumulator()

app = FastAPI()

conversation_history_path = Path(__file__).parent / 'conversations' / 'user.json'

SERVER_LOCAL_PORT = int(os.getenv('SERVER_LOCAL_PORT', 8000))


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

        force_task_completion_message = """AUTOMATED MESSAGE: Proceed. You CAN run code on my machine. If you want to run code, start your message with "```"! If the entire task I asked for is done, say exactly 'The task is done.' If you need some specific information (like username or password) say EXACTLY 'Please provide more information.' If it's impossible, say 'The task is impossible.' (If I haven't provided a task, say exactly 'Let me know what you'd like to do next.') Otherwise keep going."""
        interpreter.messages = [m for m in interpreter.messages if m["content"] != force_task_completion_message]
        insert_force_task_completion_message = True

        if any([m["type"] == "image" for m in messages]) and interpreter.llm.model.startswith("gpt-"):
            interpreter.llm.model = "gpt-4-vision-preview"
            interpreter.llm.supports_vision = True

        while insert_force_task_completion_message == True:
            
            for chunk in interpreter.chat(messages, stream=True, display=True):

                if chunk["type"] == "code":
                    insert_force_task_completion_message = False

                if any([m["type"] == "image" for m in interpreter.messages]):
                    interpreter.llm.model = "gpt-4-vision-preview"

                logger.debug("Got chunk:", chunk)

                # Send it to the user
                await to_device.put(chunk)
                # Yield to the event loop, so you actually send it out
                await asyncio.sleep(0.01)
                
                if os.getenv('TTS_RUNNER') == "server":
                    # Speak full sentences out loud
                    if chunk["role"] == "assistant" and "content" in chunk and chunk["type"] == "message":
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
                    
                    if type(temp_message) is dict and temp_message.get("role") == "user" and temp_message.get("end"):
                        # Yup. False alarm.
                        continue
                    else:
                        # Whoops! Put that back
                        await from_user.put(temp_message)

                    with open(conversation_history_path, 'w') as file:
                        json.dump(interpreter.messages, file, indent=4)

                    # TODO: is triggering seemingly randomly
                    #logger.info("New user message recieved. Breaking.")
                    #break

                # Also check if there's any new computer messages
                if not from_computer.empty():
                    
                    with open(conversation_history_path, 'w') as file:
                        json.dump(interpreter.messages, file, indent=4)

                    logger.info("New computer message recieved. Breaking.")
                    break
            else:
                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file, indent=4)

                force_task_completion_responses = [
                    "the task is done.",
                    "the task is impossible.",
                    "let me know what you'd like to do next.",
                    "please provide more information.",
                ]

                # Did the LLM respond with one of the key messages?
                if (
                    interpreter.messages
                    and any(
                        task_status in interpreter.messages[-1].get("content", "").lower()
                        for task_status in force_task_completion_responses
                    )
                ):
                    insert_force_task_completion_message = False
                    break
                
                if insert_force_task_completion_message:
                    interpreter.messages += [
                        {
                            "role": "user",
                            "type": "message",
                            "content": force_task_completion_message,
                        }
                    ]
                else:
                    break

async def stream_tts_to_device(sentence):
    force_task_completion_responses = [
        "the task is done",
        "the task is impossible",
        "let me know what you'd like to do next",
    ]
    if sentence.lower().strip().strip(".!?").strip() in force_task_completion_responses:
        return
    for chunk in stream_tts(sentence):
        await to_device.put(chunk)

from uvicorn import Config, Server

# Run the FastAPI app
if __name__ == "__main__":

    async def main():
        if os.getenv('TEACH_MODE') == "True":
            teach()
        else:
            # Start listening
            asyncio.create_task(listener())

            # Start watching the kernel if it's your job to do that
            if os.getenv('CODE_RUNNER') == "server":
                asyncio.create_task(put_kernel_messages_into_queue(from_computer))
                
            # Start the server
            logger.info("Starting `server.py`... on localhost:" + str(SERVER_LOCAL_PORT))

            config = Config(app, host="localhost", port=SERVER_LOCAL_PORT, lifespan='on')
            server = Server(config)
            await server.serve()

    asyncio.run(main())