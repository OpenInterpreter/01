import ffmpeg
import tempfile
from openai import OpenAI
import os
import subprocess
import tempfile

client = OpenAI()

class Tts:
    def __init__(self, config):
        pass

    def tts(self, text):
            response = client.audio.speech.create(
                model="tts-1",
                voice=os.getenv('OPENAI_VOICE_NAME', 'alloy'),
                input=text,
                response_format="opus"
            )
            with tempfile.NamedTemporaryFile(suffix=".opus", delete=False) as temp_file:
                response.stream_to_file(temp_file.name)

                # TODO: hack to format audio correctly for device
                outfile = tempfile.gettempdir() + "/" + "raw.dat"
                ffmpeg.input(temp_file.name).output(outfile, f="s16le", ar="16000", ac="1", loglevel='panic').run()

                return outfile


