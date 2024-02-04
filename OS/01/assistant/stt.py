"""
Defines a function which takes a path to an audio file and turns it into text.
"""

from datetime import datetime
import os
import contextlib
import tempfile
import ffmpeg
import subprocess

from openai import OpenAI
client = OpenAI()

def convert_mime_type_to_format(mime_type: str) -> str:
    if mime_type == "audio/x-wav" or mime_type == "audio/wav":
        return "wav"
    if mime_type == "audio/webm":
        return "webm"

    return mime_type

@contextlib.contextmanager
def export_audio_to_wav_ffmpeg(audio: bytearray, mime_type: str) -> str:
    temp_dir = tempfile.gettempdir()

    # Create a temporary file with the appropriate extension
    input_ext = convert_mime_type_to_format(mime_type)
    input_path = os.path.join(temp_dir, f"input_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.{input_ext}")
    with open(input_path, 'wb') as f:
        f.write(audio)

    # Export to wav
    output_path = os.path.join(temp_dir, f"output_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav")
    ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le', ac=1, ar='16k').run()

    print(f"Temporary file path: {output_path}")

    try:
        yield output_path
    finally:
        os.remove(input_path)
        os.remove(output_path)


def stt(audio_bytes: bytearray, mime_type):
    with export_audio_to_wav_ffmpeg(audio_bytes, mime_type) as wav_file_path:
        audio_file = open(wav_file_path, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
        )

        print("Exciting transcription result:", transcript)
        return transcript
