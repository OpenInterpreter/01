"""
Defines a function which takes text and returns a path to an audio file.
"""

from openai import OpenAI

client = OpenAI()

def tts(text, file_path):

    response = client.with_streaming_response.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    response.stream_to_file(file_path)
    