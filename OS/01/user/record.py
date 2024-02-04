"""
Handles everything the user interacts through.

Connects to a websocket at /user. Sends shit to it, and displays/plays the shit it sends back.

For now, just handles a spacebar being pressed— for the duration it's pressed,
it should record audio.

SIMPLEST POSSIBLE: Sends that audio to OpenAI whisper, gets the transcript,
sends it to /user in LMC format (role: user, etc)

MOST FUTUREPROOF: Streams chunks of audio to /user, which will then handle stt in stt.py.
"""

import os
import pyaudio
import threading
import asyncio
import websockets
import json
from pynput import keyboard
import wave
import tempfile
from datetime import datetime

# Configuration
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1  # Stereo
fs = 48000 # Sample rate

p = pyaudio.PyAudio()  # Create an interface to PortAudio
frames = []  # Initialize array to store frames
recording = False  # Flag to control recording state

ws_chunk_size = 4096 # Websocket stream chunk size

async def start_recording():
    global recording

    if recording:
        return  # Avoid multiple starts
    recording = True
    frames.clear()  # Clear existing frames

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    print("Recording started...")
    async with websockets.connect("ws://localhost:8000/user") as websocket:
        # Send the start command with mime type
        await websocket.send(json.dumps({"role": "user", "type": "audio", "format": "audio/wav", "start": True}))
        while recording:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        try:
            file_path = save_recording(frames)
            with open(file_path, 'rb') as audio_file:
                byte_chunk = audio_file.read(ws_chunk_size)
                while byte_chunk:
                    await websocket.send({"role": "user", "type": "audio", "format": "audio/wav", "content": byte_chunk})
                    byte_chunk = audio_file.read(ws_chunk_size)
        finally:
            os.remove(file_path)

        # Send the end command
        await websocket.send(json.dumps({"role": "user", "type": "audio", "format": "audio/wav", "end": True}))

        # Receive a json message and then close the connection
        message = await websocket.recv()
        print("Received message:", json.loads(message))

    print("Recording stopped.")

def save_recording(frames) -> str:
    # Save the recorded data as a WAV file
    temp_dir = tempfile.gettempdir()

    # Create a temporary file with the appropriate extension
    output_path = os.path.join(temp_dir, f"input_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav")
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    return output_path

def start_recording_sync():
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asyncio event loop
    loop.run_until_complete(start_recording())
    loop.close()

def stop_recording():
    global recording
    recording = False
    print("Stopped recording")

def toggle_recording():
    global recording
    if recording:
        stop_recording()
    else:
        # Start recording in a new thread to avoid blocking
        print("Starting recording")
        threading.Thread(target=start_recording_sync).start()

is_space_pressed = False  # Flag to track the state of the spacebar

def on_press(key):
    global is_space_pressed
    if key == keyboard.Key.space and not is_space_pressed:
        is_space_pressed = True
        toggle_recording()

def on_release(key):
    global is_space_pressed
    if key == keyboard.Key.space and is_space_pressed:
        is_space_pressed = False
        stop_recording()
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    with tempfile.TemporaryDirectory():
        print("Press the spacebar to start/stop recording. Press ESC to exit.")
        listener.join()

p.terminate()