"""
Defines a function which takes text and returns a path to an audio file.
"""

from pydub import AudioSegment
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import tempfile
from openai import OpenAI
import os
import subprocess
import tempfile
from pydub import AudioSegment

client = OpenAI()

chunk_size = 1024

def stream_tts(text):
    """
    A generator that streams tts as LMC messages.
    """
    if os.getenv('ALL_LOCAL') == 'False':
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="opus"
        )
        with tempfile.NamedTemporaryFile(suffix=".opus") as temp_file:
            response.stream_to_file(temp_file.name)

            audio_bytes = temp_file.read()
            file_type = "bytes.opus"

    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_file = temp_file.name
            piper_dir = os.path.join(os.path.dirname(__file__), 'local_service', 'piper')
            subprocess.run([
                os.path.join(piper_dir, 'piper'),
                '--model', os.path.join(piper_dir, os.getenv('PIPER_VOICE_NAME')),
                '--output_file', output_file
            ], input=text, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            audio_bytes = temp_file.read()
            file_type = "bytes.wav"

    # Stream the audio
    yield {"role": "assistant", "type": "audio", "format": file_type, "start": True}
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i+chunk_size]
        yield chunk
    yield {"role": "assistant", "type": "audio", "format": file_type, "end": True}

def play_audiosegment(audio):
    """
    UNUSED
    the default makes some pops. this fixes that
    """

    # Apply a fade-out (optional but recommended to smooth the end)
    audio = audio.fade_out(500)

    # Add silence at the end
    silence_duration_ms = 500  # Duration of silence in milliseconds
    silence = AudioSegment.silent(duration=silence_duration_ms)
    audio_with_padding = audio + silence

    # Save the modified audio as a WAV file for compatibility with simpleaudio
    audio_with_padding.export("output_audio.wav", format="wav")

    # Load the processed WAV file
    wave_obj = sa.WaveObject.from_wave_file("output_audio.wav")

    # Play the audio
    play_obj = wave_obj.play()

    # Wait for the playback to finish
    play_obj.wait_done()

    # Delete the wav file
    os.remove("output_audio.wav")

