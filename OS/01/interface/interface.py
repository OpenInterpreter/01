import redis
import RPi.GPIO as GPIO
import asyncio
import websockets
import sounddevice as sd
import numpy as np
import time
import re

def transcribe(audio_chunks):
    pass # (todo)

def say(text):
    # This should immediatly stop if button is pressed (if GPIO.input(18))
    pass # (todo)

# Connect to button
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set the duration and sample rate for the mic
chunk_duration = 0.5  # seconds
sample_rate = 44100  # Hz

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Define some standard, useful messages
user_start_message = {"role": "user", "type": "message", "start": True}
user_start_message = {"role": "user", "type": "message", "start": True}

# Set up websocket connection
websocket = websockets.connect('ws://localhost:8765')

# This is so we only say() full sentences
accumulated_text = ""
def is_full_sentence(text):
    return text.endswith(('.', '!', '?'))
def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

async def send_to_websocket(message):
    async with websocket as ws:
        await ws.send(message)

async def check_websocket():
    async with websocket as ws:
        message = await ws.recv()
        return message

def main():
    while True:

        # If the button is pushed down
        if not GPIO.input(18):

            # Send start message to core and websocket
            r.rpush('to_core', user_start_message)
            send_to_websocket(user_start_message)

            # Record audio from the microphone in chunks
            audio_chunks = []

            # Continue recording until the button is released
            while not GPIO.input(18):
                chunk = sd.rec(int(chunk_duration * sample_rate), samplerate=sample_rate, channels=2)
                sd.wait()  # Wait until recording is finished
                audio_chunks.append(chunk)

            # Transcribe
            text = transcribe(audio_chunks)

            message = {"role": "user", "type": "message", "content": text, "time": time.time()}

            # Send message to core and websocket
            r.rpush('to_core', message)
            send_to_websocket(message)
        
        # Send out anything in the to_interface queue
        chunk = r.lpop('to_interface')
        if chunk:
            send_to_websocket(chunk)
            accumulated_text += chunk["content"]
            
            # Speak full sentences out loud
            sentences = split_into_sentences(accumulated_text)
            if is_full_sentence(sentences[-1]):
                for sentence in sentences:
                    say(sentence)
                accumulated_text = ""
            else:
                for sentence in sentences[:-1]:
                    say(sentence)
                accumulated_text = sentences[-1]
        else:
            say(accumulated_text)
            accumulated_text = ""

        message = check_websocket()
        if message:
            r.rpush('to_core', message)

if __name__ == "__main__":
    main()
