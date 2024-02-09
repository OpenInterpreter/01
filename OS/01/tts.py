"""
Defines a function which takes text and returns a path to an audio file.
"""

import tempfile
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound

client = OpenAI()

def tts(text, play_audio):
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
