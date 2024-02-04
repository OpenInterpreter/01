import asyncio
import threading
import os
import pyaudio
from starlette.websockets import WebSocket
from queue import Queue
from pynput import keyboard
import json
import websockets
import queue
import pydub
import ast

# Configuration for Audio Recording
CHUNK = 1024  # Record in chunks of 1024 samples
FORMAT = pyaudio.paInt16  # 16 bits per sample
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
RECORDING = False  # Flag to control recording state
SPACEBAR_PRESSED = False  # Flag to track spacebar press state

# Configuration for WebSocket
PORT = os.getenv('ASSISTANT_PORT', '8000')
WS_URL = f"ws://localhost:{PORT}/user"

# Initialize PyAudio
p = pyaudio.PyAudio()


import wave
import tempfile
from datetime import datetime


def record_audio():
    """Record audio from the microphone and add it to the queue."""
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording started...")
    global RECORDING

    # Create a temporary WAV file to store the audio data
    temp_dir = tempfile.gettempdir()
    wav_path = os.path.join(temp_dir, f"audio_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav")
    wav_file = wave.open(wav_path, 'wb')
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(p.get_sample_size(FORMAT))
    wav_file.setframerate(RATE)

    while RECORDING:
        data = stream.read(CHUNK, exception_on_overflow=False)
        wav_file.writeframes(data)

    wav_file.close()
    stream.stop_stream()
    stream.close()
    print("Recording stopped.")

    # After recording is done, read and stream the audio file in chunks
    with open(wav_path, 'rb') as audio_file:
        byte_data = audio_file.read(CHUNK)
        while byte_data:
            send_queue.put({"role": "user", "type": "audio", "format": "audio/wav", "content": str(byte_data)})
            byte_data = audio_file.read(CHUNK)

    send_queue.put({"role": "user", "type": "audio", "format": "audio/wav", "end": True})


def toggle_recording(state):
    """Toggle the recording state."""
    global RECORDING, SPACEBAR_PRESSED
    if state and not SPACEBAR_PRESSED:
        SPACEBAR_PRESSED = True
        if not RECORDING:
            RECORDING = True
            threading.Thread(target=record_audio).start()
    elif not state and SPACEBAR_PRESSED:
        SPACEBAR_PRESSED = False
        RECORDING = False

def on_press(key):
    """Detect spacebar press."""
    if key == keyboard.Key.space:
        toggle_recording(True)

def on_release(key):
    """Detect spacebar release and ESC key press."""
    if key == keyboard.Key.space:
        toggle_recording(False)
    elif key == keyboard.Key.esc:
        print("Exiting...")
        os._exit(0)

import asyncio

send_queue = queue.Queue()

async def message_sender(websocket):
    while True:
        message = await asyncio.get_event_loop().run_in_executor(None, send_queue.get)
        await websocket.send(json.dumps(message))
        send_queue.task_done()

async def websocket_communication(WS_URL):
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                print("Press the spacebar to start/stop recording. Press ESC to exit.")
                asyncio.create_task(message_sender(websocket))

                async for message in websocket:
                    print(message)
                    await asyncio.sleep(1)
        except:
            print("Connecting...")
            await asyncio.sleep(2)

def main():
    # Start the WebSocket communication in a separate asyncio event loop
    ws_thread = threading.Thread(target=lambda: asyncio.run(websocket_communication(WS_URL)), daemon=True)
    ws_thread.start()

    # Keyboard listener for spacebar press/release
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    p.terminate()

if __name__ == "__main__":
    main()
