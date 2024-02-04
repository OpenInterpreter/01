"""
Exposes a POST endpoint called /computer. Things from there go into the queue.

Exposes a ws endpoint called /user. Things from there go into the queue. We also send things in the queue back (that are role: assistant)

In a while loop we watch the queue and handle it.
"""

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
from create_interpreter import create_interpreter
from stt import stt
from tts import tts
from pathlib import Path

# Create interpreter
interpreter = create_interpreter()

conversation_history_path = Path(__file__).parent / 'conversations' / 'user.json'



# This is so we only say() full sentences
def is_full_sentence(text):
    return text.endswith(('.', '!', '?'))

def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

app = FastAPI()



import asyncio


# Global queues
receive_queue = queue.Queue()
send_queue = queue.Queue()


@app.websocket("/user")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    receive_task = asyncio.create_task(receive_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket))
    await asyncio.gather(receive_task, send_task)

async def receive_messages(websocket: WebSocket):
    while True:
        data = await websocket.receive_text()
        receive_queue.put(data)

async def send_messages(websocket: WebSocket):
    while True:
        message = await asyncio.get_event_loop().run_in_executor(None, send_queue.get)
        print(message)
        await websocket.send_json(message)
            






@app.post("/computer")
async def read_computer(item: dict):
    await asyncio.get_event_loop().run_in_executor(None, receive_queue.put, item)













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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('ASSISTANT_PORT', 8000)))
