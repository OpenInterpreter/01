from RealtimeTTS import TextToAudioStream, CoquiEngine, OpenAIEngine, ElevenlabsEngine
from fastapi.responses import PlainTextResponse
from RealtimeSTT import AudioToTextRecorder
import importlib
import asyncio
import types
import wave
import os

os.environ["INTERPRETER_REQUIRE_ACKNOWLEDGE"] = "False"

def start_server(server_host, server_port, profile, debug, play_audio):

    # Load the profile module from the provided path
    spec = importlib.util.spec_from_file_location("profile", profile)
    profile_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile_module)

    # Get the interpreter from the profile
    interpreter = profile_module.interpreter

    # STT
    interpreter.stt = AudioToTextRecorder(
        model="tiny.en", spinner=False, use_microphone=False
    )
    interpreter.stt.stop()  # It needs this for some reason

    # TTS
    if not hasattr(interpreter, 'tts'):
        print("Setting TTS provider to default: openai")
        interpreter.tts = "openai"
    if interpreter.tts == "coqui":
        engine = CoquiEngine()
    elif interpreter.tts == "openai":
        engine = OpenAIEngine(voice="onyx")
    elif interpreter.tts == "elevenlabs":
        engine = ElevenlabsEngine(api_key=os.environ["ELEVEN_LABS_API_KEY"])
        engine.set_voice("Michael")
    else:
        raise ValueError(f"Unsupported TTS engine: {interpreter.interpreter.tts}")
    interpreter.tts = TextToAudioStream(engine)

    # Misc Settings
    interpreter.verbose = debug
    interpreter.server.host = server_host
    interpreter.server.port = server_port
    interpreter.play_audio = play_audio
    interpreter.audio_chunks = []


    ### Swap out the input function for one that supports voice

    old_input = interpreter.input

    async def new_input(self, chunk):
        await asyncio.sleep(0)
        if isinstance(chunk, bytes):
            self.stt.feed_audio(chunk)
            self.audio_chunks.append(chunk)
        elif isinstance(chunk, dict):
            if "start" in chunk:
                self.stt.start()
                self.audio_chunks = []
                await old_input({"role": "user", "type": "message", "start": True})
            if "end" in chunk:
                self.stt.stop()
                content = self.stt.text()

                print("\n\nUser: ", content)

                if False:
                    audio_bytes = bytearray(b"".join(self.audio_chunks))
                    with wave.open('audio.wav', 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)  # Assuming 16-bit audio
                        wav_file.setframerate(16000)  # Assuming 16kHz sample rate
                        wav_file.writeframes(audio_bytes)
                    print(os.path.abspath('audio.wav'))

                await old_input({"role": "user", "type": "message", "content": content})
                await old_input({"role": "user", "type": "message", "end": True})


    ### Swap out the output function for one that supports voice

    old_output = interpreter.output

    async def new_output(self):
        while True:
            output = await old_output()
            # if output == {"role": "assistant", "type": "message", "start": True}:
            #     return {"role": "assistant", "type": "audio", "format": "bytes.wav", "start": True}

            if isinstance(output, bytes):
                return output

            await asyncio.sleep(0)

            delimiters = ".?!;,\n…)]}"

            if output["type"] == "message" and len(output.get("content", "")) > 0:

                self.tts.feed(output.get("content"))

                if not self.tts.is_playing() and any([c in delimiters for c in output.get("content")]): # Start playing once the first delimiter is encountered.
                    self.tts.play_async(on_audio_chunk=self.on_tts_chunk, muted=not self.play_audio, sentence_fragment_delimiters=delimiters, minimum_sentence_length=9)
                    return {"role": "assistant", "type": "audio", "format": "bytes.wav", "start": True}

            if output == {"role": "assistant", "type": "message", "end": True}:
                if not self.tts.is_playing(): # We put this here in case it never outputs a delimiter and never triggers play_async^
                    self.tts.play_async(on_audio_chunk=self.on_tts_chunk, muted=not self.play_audio, sentence_fragment_delimiters=delimiters, minimum_sentence_length=9)
                    return {"role": "assistant", "type": "audio", "format": "bytes.wav", "start": True}
                return {"role": "assistant", "type": "audio", "format": "bytes.wav", "end": True}

    def on_tts_chunk(self, chunk):
        self.output_queue.sync_q.put(chunk)


    # Set methods on interpreter object
    interpreter.input = types.MethodType(new_input, interpreter)
    interpreter.output = types.MethodType(new_output, interpreter)
    interpreter.on_tts_chunk = types.MethodType(on_tts_chunk, interpreter)

    # Add ping route, required by device
    @interpreter.server.app.get("/ping")
    async def ping():
        return PlainTextResponse("pong")

    # Start server
    interpreter.server.run()