from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import asyncio
import threading
import os
import pyaudio
from starlette.websockets import WebSocket
from queue import Queue
from pynput import keyboard
import json
import traceback
import websockets
import queue
import pydub
import ast
from pydub import AudioSegment
from pydub.playback import play
import io
import time
import wave
import tempfile
from datetime import datetime
from interpreter import interpreter # Just for code execution. Maybe we should let people do from interpreter.computer import run?
# In the future, I guess kernel watching code should be elsewhere? Somewhere server / client agnostic?
from ..server.utils.kernel import put_kernel_messages_into_queue
from ..server.utils.get_system_info import get_system_info
from ..server.stt.stt import stt_wav

from ..server.utils.logs import setup_logging
from ..server.utils.logs import logger
setup_logging()


from ..utils.accumulator import Accumulator

accumulator = Accumulator()

# Configuration for Audio Recording
CHUNK = 1024  # Record in chunks of 1024 samples
FORMAT = pyaudio.paInt16  # 16 bits per sample
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
RECORDING = False  # Flag to control recording state
SPACEBAR_PRESSED = False  # Flag to track spacebar press state

# Specify OS
current_platform = get_system_info()

# Initialize PyAudio
p = pyaudio.PyAudio()

send_queue = queue.Queue()

class Device:
    def __init__(self):
        self.audiosegments = []
        pass

    async def play_audiosegments(self):
        """Plays them sequentially."""
        while True:
            try:
                for audio in self.audiosegments:
                    play(audio)
                    self.audiosegments.remove(audio)
                await asyncio.sleep(0.1)
            except:
                traceback.print_exc()


    def record_audio(self):
        
        if os.getenv('STT_RUNNER') == "server":
            # STT will happen on the server. we're sending audio.
            send_queue.put({"role": "user", "type": "audio", "format": "bytes.wav", "start": True})
        elif os.getenv('STT_RUNNER') == "client":
            # STT will happen here, on the client. we're sending text.
            send_queue.put({"role": "user", "type": "message", "start": True})
        else:
            raise Exception("STT_RUNNER must be set to either 'client' or 'server'.")

        """Record audio from the microphone and add it to the queue."""
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        logger.info("Recording started...")
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
        logger.info("Recording stopped.")

        duration = wav_file.getnframes() / RATE
        if duration < 0.3:
            # Just pressed it. Send stop message
            if os.getenv('STT_RUNNER') == "client":
                send_queue.put({"role": "user", "type": "message", "content": "stop"})
                send_queue.put({"role": "user", "type": "message", "end": True})
            else:
                send_queue.put({"role": "user", "type": "audio", "format": "bytes.wav", "content": ""})
                send_queue.put({"role": "user", "type": "audio", "format": "bytes.wav", "end": True})
        else:
            if os.getenv('STT_RUNNER') == "client":
                # Run stt then send text
                text = stt_wav(wav_path)
                send_queue.put({"role": "user", "type": "message", "content": text})
                send_queue.put({"role": "user", "type": "message", "end": True})
            else:
                # Stream audio
                with open(wav_path, 'rb') as audio_file:
                    byte_data = audio_file.read(CHUNK)
                    while byte_data:
                        send_queue.put(byte_data)
                        byte_data = audio_file.read(CHUNK)
                send_queue.put({"role": "user", "type": "audio", "format": "bytes.wav", "end": True})

        if os.path.exists(wav_path):
            os.remove(wav_path)

    def toggle_recording(self, state):
        """Toggle the recording state."""
        global RECORDING, SPACEBAR_PRESSED
        if state and not SPACEBAR_PRESSED:
            SPACEBAR_PRESSED = True
            if not RECORDING:
                RECORDING = True
                threading.Thread(target=self.record_audio).start()
        elif not state and SPACEBAR_PRESSED:
            SPACEBAR_PRESSED = False
            RECORDING = False

    def on_press(self, key):
        """Detect spacebar press."""
        if key == keyboard.Key.space:
            self.toggle_recording(True)

    def on_release(self, key):
        """Detect spacebar release and ESC key press."""
        if key == keyboard.Key.space:
            self.toggle_recording(False)
        elif key == keyboard.Key.esc or (key == keyboard.Key.ctrl and keyboard.Key.c):
            logger.info("Exiting...")
            os._exit(0)

    async def message_sender(self, websocket):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, send_queue.get)
            if isinstance(message, bytes):
                await websocket.send(message)
            else:
                await websocket.send(json.dumps(message))
            send_queue.task_done()
            await asyncio.sleep(0.01)

    async def websocket_communication(self, WS_URL):
        while True:
            try:
                async with websockets.connect(WS_URL) as websocket:
                    logger.info("Press the spacebar to start/stop recording. Press ESC to exit.")
                    asyncio.create_task(self.message_sender(websocket))

                    while True:
                        await asyncio.sleep(0.01)
                        chunk = await websocket.recv()

                        logger.debug(f"Got this message from the server: {type(chunk)} {chunk}")

                        if type(chunk) == str:
                            chunk = json.loads(chunk)

                        message = accumulator.accumulate(chunk)
                        if message == None:
                            # Will be None until we have a full message ready
                            continue

                        # At this point, we have our message

                        if message["type"] == "audio" and message["format"].startswith("bytes"):

                            # Convert bytes to audio file
                            # Format will be bytes.wav or bytes.opus
                            audio_bytes = io.BytesIO(message["content"])
                            audio = AudioSegment.from_file(audio_bytes, codec=message["format"].split(".")[1])

                            self.audiosegments.append(audio)

                        # Run the code if that's the client's job
                        if os.getenv('CODE_RUNNER') == "client":
                            if message["type"] == "code" and "end" in message:
                                language = message["format"]
                                code = message["content"]
                                result = interpreter.computer.run(language, code)
                                send_queue.put(result)
    

            except:
                traceback.print_exc()
                logger.info(f"Connecting to `{WS_URL}`...")
                await asyncio.sleep(2)

    async def start_async(self):
            # Configuration for WebSocket
            WS_URL = os.getenv('SERVER_URL')
            if not WS_URL:
                raise ValueError("The environment variable SERVER_URL is not set. Please set it to proceed.")

            # Start the WebSocket communication
            asyncio.create_task(self.websocket_communication(WS_URL))

            # Start watching the kernel if it's your job to do that
            if os.getenv('CODE_RUNNER') == "client":
                asyncio.create_task(put_kernel_messages_into_queue(send_queue))

            asyncio.create_task(self.play_audiosegments())
            
            # If Raspberry Pi, add the button listener, otherwise use the spacebar
            if current_platform.startswith("raspberry-pi"):
                logger.info("Raspberry Pi detected, using button on GPIO pin 15")
                # Use GPIO pin 15
                pindef = ["gpiochip4", "15"] # gpiofind PIN15
                print("PINDEF", pindef)

                # HACK: needs passwordless sudo
                process = await asyncio.create_subprocess_exec("sudo", "gpiomon", "-brf", *pindef, stdout=asyncio.subprocess.PIPE)
                while True:
                    line = await process.stdout.readline()
                    if line:
                        line = line.decode().strip()
                        if "FALLING" in line:
                            self.toggle_recording(False)
                        elif "RISING" in line:
                            self.toggle_recording(True)
                    else:
                        break
            else:
                # Keyboard listener for spacebar press/release
                listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
                listener.start()

    def start(self):
        asyncio.run(self.start_async())
        p.terminate()