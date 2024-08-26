import asyncio
import websockets
import pyaudio
from pynput import keyboard
import json
from yaspin import yaspin

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORDING_RATE = 16000
PLAYBACK_RATE = 24000

class Device:
    def __init__(self):
        self.server_url = "0.0.0.0:10001"
        self.p = pyaudio.PyAudio()
        self.websocket = None
        self.recording = False
        self.input_stream = None
        self.output_stream = None
        self.spinner = yaspin()
        self.play_audio = True

    async def connect_with_retry(self, max_retries=50, retry_delay=2):
        for attempt in range(max_retries):
            try:
                self.websocket = await websockets.connect(f"ws://{self.server_url}")

                # Send auth, which the server requires (docs.openinterpreter.com/server/usage)
                await self.websocket.send(json.dumps({"auth": True}))

                return
            except ConnectionRefusedError:
                if attempt % 8 == 0 and attempt != 0:
                    print(f"Loading...")
                await asyncio.sleep(retry_delay)
        raise Exception("Failed to connect to the server after multiple attempts")

    async def send_audio(self):
        self.input_stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RECORDING_RATE, input=True, frames_per_buffer=CHUNK)
        while True:
            if self.recording:
                try:
                    # Send start flag
                    await self.websocket.send(json.dumps({"role": "user", "type": "audio", "format": "bytes.wav", "start": True}))
                    # print("Sending audio start message")
                    
                    while self.recording:
                        data = self.input_stream.read(CHUNK, exception_on_overflow=False)
                        await self.websocket.send(data)
                    
                    # Send stop flag
                    await self.websocket.send(json.dumps({"role": "user", "type": "audio", "format": "bytes.wav", "end": True}))
                    # print("Sending audio end message")
                except Exception as e:
                    print(f"Error in send_audio: {e}")
            await asyncio.sleep(0.01)

    async def receive_audio(self):
        self.output_stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=PLAYBACK_RATE, output=True, frames_per_buffer=CHUNK)
        while True:
            try:
                data = await self.websocket.recv()
                if self.play_audio and isinstance(data, bytes) and not self.recording:
                    self.output_stream.write(data)
            except Exception as e:
                await self.connect_with_retry()

    def on_press(self, key):
        if key == keyboard.Key.ctrl and not self.recording:
            #print("Space pressed, starting recording")
            print("")
            self.spinner.start()
            self.recording = True

    def on_release(self, key):
        if key == keyboard.Key.ctrl: # TODO: Pass in hotkey
            self.spinner.stop()
            #print("Space released, stopping recording")
            self.recording = False
        # elif key == keyboard.Key.esc:
        #     print("Esc pressed, stopping the program")
        #     return False

    async def main(self):
        await self.connect_with_retry()
        print("\nHold CTRL to speak to your assistant. Press 'CTRL-C' to quit.")
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        await asyncio.gather(self.send_audio(), self.receive_audio())

    def start(self):
        asyncio.run(self.main())

def run(server_url, debug):
    device = Device()
    device.server_url = server_url
    device.debug = debug
    device.start()