"""
Defines a function which takes text and returns a path to an audio file.
"""

from openai import OpenAI
import pydub
import pydub.playback
import tempfile
import os
from datetime import datetime
from io import BytesIO

client = OpenAI()
chunk_size = 1024
read_chunk_size = 4096

def tts(text):

    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"output_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.mp3")

    try:
        with (
            client.with_streaming_response.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format='mp3',
            speed=1.2)
        ) as response:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_bytes(chunk_size):                    
                    f.write(chunk)
        
        with open(output_path, 'rb') as f:
            byte_chunk = f.read(read_chunk_size)
            yield byte_chunk

        seg = pydub.AudioSegment.from_mp3(output_path)
        pydub.playback.play(seg)
    finally:
        os.remove(output_path)