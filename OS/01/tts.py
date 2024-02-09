"""
Defines a function which takes text and returns a path to an audio file.
"""

import tempfile
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play

client = OpenAI()

def tts(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3"
    )
    with tempfile.NamedTemporaryFile() as temp_file:
        response.stream_to_file(temp_file.name)
        
        audio = AudioSegment.from_file(temp_file.name, format="mp3")
        # Gradual fade in and out over 0.2 seconds
        audio = audio.fade_in(200).fade_out(200)
        play(audio)
        
        return temp_file.read()
