"""
Defines a function which takes text and returns a path to an audio file.
"""

import tempfile
from openai import OpenAI

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
        return temp_file.read()
