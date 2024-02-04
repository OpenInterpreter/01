"""
Exposes a POST endpoint called /computer. Things from there go into the queue.

Exposes a ws endpoint called /user. Things from there go into the queue. We also send things in the queue back (that are role: assistant)

In a while loop we watch the queue.
"""

import json
import time
import queue
import os
from threading import Thread
import uvicorn
import re
from fastapi import FastAPI
from threading import Thread
from starlette.websockets import WebSocket
from create_interpreter import create_interpreter
from stt import stt
from tts import tts

# Create interpreter
interpreter = create_interpreter()

script_dir = os.path.dirname(os.path.abspath(__file__))
conversation_history_path = os.path.join(script_dir, 'conversations', 'user.json')

# Create Queue objects
to_user = queue.Queue()
to_assistant = queue.Queue()

# This is so we only say() full sentences
accumulated_text = ""
def is_full_sentence(text):
    return text.endswith(('.', '!', '?'))
def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

app = FastAPI()

@app.post("/computer")
async def read_computer(item: dict):
    to_assistant.put(item)

@app.websocket("/user")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        to_assistant.put(data)
        if not to_user.empty():
            message = to_user.get()
            await websocket.send_json(message)

audio_chunks = []

def queue_listener():
    while True:
        # Check 10x a second for new messages
        while to_assistant.empty():
            time.sleep(0.1)
        message = to_assistant.get()

        # Hold the audio in a buffer. If it's ready (we got end flag, stt it)
        if message["type"] == "audio":
            if "content" in message:
                audio_chunks.append(message)
            if "end" in message:
                text = stt(audio_chunks)
                audio_chunks = []
                message = {"role": "user", "type": "message", "content": text}
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
        
        for chunk in interpreter.chat(messages):

            # Send it to the user
            to_user.put(chunk)
            
            # Speak full sentences out loud
            accumulated_text += chunk["content"]
            sentences = split_into_sentences(accumulated_text)
            if is_full_sentence(sentences[-1]):
                for sentence in sentences:
                    for audio_chunk in tts(sentence):
                        to_user.put(audio_chunk)
                accumulated_text = ""
            else:
                for sentence in sentences[:-1]:
                    for audio_chunk in tts(sentence):
                        to_user.put(audio_chunk)
                accumulated_text = sentences[-1]

            if chunk["type"] == "message" and "content" in sentence:
                sentence += chunk.get("content")
            
            # If we have a new message, save our progress and go back to the top
            if not to_assistant.empty():
                with open(conversation_history_path, 'w') as file:
                    json.dump(interpreter.messages, file)
                break

# Create a thread for the queue listener
queue_thread = Thread(target=queue_listener)

# Start the queue listener thread
queue_thread.start()

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)