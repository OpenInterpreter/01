"""
Defines a function which takes text and returns a path to an audio file.
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import tempfile
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
import os
import subprocess
import tempfile

client = OpenAI()

def tts(text, play_audio):
    if os.getenv('ALL_LOCAL') == 'False':
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3"
        )
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            response.stream_to_file(temp_file.name)
            
            if play_audio:
                playsound(temp_file.name)
            
            return temp_file.read()
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_file = temp_file.name
            piper_dir = os.path.join(os.path.dirname(__file__), 'local_tts', 'piper')
            subprocess.run([
                os.path.join(piper_dir, 'piper'),
                '--model', os.path.join(piper_dir, os.getenv('PIPER_VOICE_NAME')),
                '--output_file', output_file
            ], input=text, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if play_audio:
                playsound(temp_file.name)
            return temp_file.read()
