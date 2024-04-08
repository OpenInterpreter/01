from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import asyncio
import threading
import pyaudio
from pynput import keyboard
import json
import traceback
import websockets
import queue
from pydub import AudioSegment
from pydub.playback import play
import time
import wave
import tempfile
from datetime import datetime
import cv2
import base64
import platform
from interpreter import (
    interpreter,
)  # Just for code execution. Maybe we should let people do from interpreter.computer import run?

# In the future, I guess kernel watching code should be elsewhere? Somewhere server / client agnostic?
from ..server.utils.kernel import put_kernel_messages_into_queue
from ..server.utils.get_system_info import get_system_info
from ..server.utils.process_utils import kill_process_tree

from ..server.utils.logs import setup_logging
from ..server.utils.logs import logger

setup_logging()

os.environ["STT_RUNNER"] = "server"
os.environ["TTS_RUNNER"] = "server"

from ..utils.accumulator import Accumulator

accumulator = Accumulator()

# Configuration for Audio Recording
CHUNK = 1024  # Record in chunks of 1024 samples
FORMAT = pyaudio.paInt16  # 16 bits per sample
CHANNELS = 1  # Mono
RATE = 44100  # Sample rate
RECORDING = False  # Flag to control recording state
SPACEBAR_PRESSED = False  # Flag to track spacebar press state

# Camera configuration
CAMERA_ENABLED = os.getenv("CAMERA_ENABLED", False)
if type(CAMERA_ENABLED) == str:
    CAMERA_ENABLED = CAMERA_ENABLED.lower() == "true"
CAMERA_DEVICE_INDEX = int(os.getenv("CAMERA_DEVICE_INDEX", 0))
CAMERA_WARMUP_SECONDS = float(os.getenv("CAMERA_WARMUP_SECONDS", 0))

# Specify OS
current_platform = get_system_info()
is_win10 = lambda: platform.system() == "Windows" and "10" in platform.version()

# Initialize PyAudio
p = pyaudio.PyAudio()

send_queue = queue.Queue()


class Device:
    def __init__(self):
        self.pressed_keys = set()
        self.captured_images = []
        self.audiosegments = []
        self.server_url = ""

    def fetch_image_from_camera(self, camera_index=CAMERA_DEVICE_INDEX):
        """Captures an image from the specified camera device and saves it to a temporary file. Adds the image to the captured_images list."""
        image_path = None

        cap = cv2.VideoCapture(camera_index)
        ret, frame = cap.read()  # Capture a single frame to initialize the camera

        if CAMERA_WARMUP_SECONDS > 0:
            # Allow camera to warm up, then snap a picture again
            # This is a workaround for some cameras that don't return a properly exposed
            # picture immediately when they are first turned on
            time.sleep(CAMERA_WARMUP_SECONDS)
            ret, frame = cap.read()

        if ret:
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(
                temp_dir, f"01_photo_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
            )
            self.captured_images.append(image_path)
            cv2.imwrite(image_path, frame)
            logger.info(f"Camera image captured to {image_path}")
            logger.info(
                f"You now have {len(self.captured_images)} images which will be sent along with your next audio message."
            )
        else:
            logger.error(
                f"Error: Couldn't capture an image from camera ({camera_index})"
            )

        cap.release()

        return image_path

    def encode_image_to_base64(self, image_path):
        """Encodes an image file to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def add_image_to_send_queue(self, image_path):
        """Encodes an image and adds an LMC message to the send queue with the image data."""
        base64_image = self.encode_image_to_base64(image_path)
        image_message = {
            "role": "user",
            "type": "image",
            "format": "base64.png",
            "content": base64_image,
        }
        send_queue.put(image_message)
        # Delete the image file from the file system after sending it
        os.remove(image_path)

    def queue_all_captured_images(self):
        """Queues all captured images to be sent."""
        for image_path in self.captured_images:
            self.add_image_to_send_queue(image_path)
        self.captured_images.clear()  # Clear the list after sending

    async def play_audiosegments(self):
        """Plays them sequentially."""
        while True:
            try:
                for audio in self.audiosegments:
                    play(audio)
                    self.audiosegments.remove(audio)
                await asyncio.sleep(0.1)
            except asyncio.exceptions.CancelledError:
                # This happens once at the start?
                pass
            except:
                logger.info(traceback.format_exc())

    def record_audio(self):
        if os.getenv("STT_RUNNER") == "server":
            # STT will happen on the server. we're sending audio.
            send_queue.put(
                {"role": "user", "type": "audio", "format": "bytes.wav", "start": True}
            )
        elif os.getenv("STT_RUNNER") == "client":
            # STT will happen here, on the client. we're sending text.
            send_queue.put({"role": "user", "type": "message", "start": True})
        else:
            raise Exception("STT_RUNNER must be set to either 'client' or 'server'.")

        """Record audio from the microphone and add it to the queue."""
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        print("Recording started...")
        global RECORDING

        # Create a temporary WAV file to store the audio data
        temp_dir = tempfile.gettempdir()
        wav_path = os.path.join(
            temp_dir, f"audio_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav"
        )
        wav_file = wave.open(wav_path, "wb")
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

        duration = wav_file.getnframes() / RATE
        if duration < 0.3:
            # Just pressed it. Send stop message
            if os.getenv("STT_RUNNER") == "client":
                send_queue.put({"role": "user", "type": "message", "content": "stop"})
                send_queue.put({"role": "user", "type": "message", "end": True})
            else:
                send_queue.put(
                    {
                        "role": "user",
                        "type": "audio",
                        "format": "bytes.wav",
                        "content": "",
                    }
                )
                send_queue.put(
                    {
                        "role": "user",
                        "type": "audio",
                        "format": "bytes.wav",
                        "end": True,
                    }
                )
        else:
            self.queue_all_captured_images()

            if os.getenv("STT_RUNNER") == "client":
                # THIS DOES NOT WORK. We moved to this very cool stt_service, llm_service
                # way of doing things. stt_wav is not a thing anymore. Needs work to work

                # Run stt then send text
                text = stt_wav(wav_path)
                logger.debug(f"STT result: {text}")
                send_queue.put({"role": "user", "type": "message", "content": text})
                send_queue.put({"role": "user", "type": "message", "end": True})
            else:
                # Stream audio
                with open(wav_path, "rb") as audio_file:
                    byte_data = audio_file.read(CHUNK)
                    while byte_data:
                        send_queue.put(byte_data)
                        byte_data = audio_file.read(CHUNK)
                send_queue.put(
                    {
                        "role": "user",
                        "type": "audio",
                        "format": "bytes.wav",
                        "end": True,
                    }
                )

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
        """Detect spacebar press and Ctrl+C combination."""
        self.pressed_keys.add(key)  # Add the pressed key to the set

        if keyboard.Key.space in self.pressed_keys:
            self.toggle_recording(True)
        elif {keyboard.Key.ctrl, keyboard.KeyCode.from_char("c")} <= self.pressed_keys:
            logger.info("Ctrl+C pressed. Exiting...")
            kill_process_tree()
            os._exit(0)

    def on_release(self, key):
        """Detect spacebar release and 'c' key press for camera, and handle key release."""
        self.pressed_keys.discard(
            key
        )  # Remove the released key from the key press tracking set

        if key == keyboard.Key.space:
            self.toggle_recording(False)
        elif CAMERA_ENABLED and key == keyboard.KeyCode.from_char("c"):
            self.fetch_image_from_camera()

    async def message_sender(self, websocket):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(
                None, send_queue.get
            )
            if isinstance(message, bytes):
                await websocket.send(message)
            else:
                await websocket.send(json.dumps(message))
            send_queue.task_done()
            await asyncio.sleep(0.01)

    async def websocket_communication(self, WS_URL):
        show_connection_log = True

        async def exec_ws_communication(websocket):
            if CAMERA_ENABLED:
                print(
                    "\nHold the spacebar to start recording. Press 'c' to capture an image from the camera. Press CTRL-C to exit."
                )
            else:
                print("\nHold the spacebar to start recording. Press CTRL-C to exit.")

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

                    audio_bytes = message["content"]

                    # Create an AudioSegment instance with the raw data
                    audio = AudioSegment(
                        # raw audio data (bytes)
                        data=audio_bytes,
                        # signed 16-bit little-endian format
                        sample_width=2,
                        # 16,000 Hz frame rate
                        frame_rate=16000,
                        # mono sound
                        channels=1,
                    )

                    self.audiosegments.append(audio)

                # Run the code if that's the client's job
                if os.getenv("CODE_RUNNER") == "client":
                    if message["type"] == "code" and "end" in message:
                        language = message["format"]
                        code = message["content"]
                        result = interpreter.computer.run(language, code)
                        send_queue.put(result)

        if is_win10():
            logger.info("Windows 10 detected")
            # Workaround for Windows 10 not latching to the websocket server.
            # See https://github.com/OpenInterpreter/01/issues/197
            try:
                ws = websockets.connect(WS_URL)
                await exec_ws_communication(ws)
            except Exception as e:
                logger.error(f"Error while attempting to connect: {e}")
        else:
            while True:
                try:
                    async with websockets.connect(WS_URL) as websocket:
                        await exec_ws_communication(websocket)
                except:
                    logger.debug(traceback.format_exc())
                    if show_connection_log:
                        logger.info(f"Connecting to `{WS_URL}`...")
                        show_connection_log = False
                        await asyncio.sleep(2)

    async def start_async(self):
        # Configuration for WebSocket
        WS_URL = f"ws://{self.server_url}"
        # Start the WebSocket communication
        asyncio.create_task(self.websocket_communication(WS_URL))

        # Start watching the kernel if it's your job to do that
        if os.getenv("CODE_RUNNER") == "client":
            asyncio.create_task(put_kernel_messages_into_queue(send_queue))

        asyncio.create_task(self.play_audiosegments())

        # If Raspberry Pi, add the button listener, otherwise use the spacebar
        if current_platform.startswith("raspberry-pi"):
            logger.info("Raspberry Pi detected, using button on GPIO pin 15")
            # Use GPIO pin 15
            pindef = ["gpiochip4", "15"]  # gpiofind PIN15
            print("PINDEF", pindef)

            # HACK: needs passwordless sudo
            process = await asyncio.create_subprocess_exec(
                "sudo", "gpiomon", "-brf", *pindef, stdout=asyncio.subprocess.PIPE
            )
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
            listener = keyboard.Listener(
                on_press=self.on_press, on_release=self.on_release
            )
            listener.start()

    def start(self):
        if os.getenv("TEACH_MODE") != "True":
            asyncio.run(self.start_async())
            p.terminate()
