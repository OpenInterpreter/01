"""
Defines a function which takes a path to an audio file and turns it into text.
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

from datetime import datetime
import os
import contextlib
import tempfile
import ffmpeg
import subprocess
import openai
from openai import OpenAI

from ..utils.logs import setup_logging
from ..utils.logs import logger
setup_logging()

client = OpenAI()

def convert_mime_type_to_format(mime_type: str) -> str:
    if mime_type == "audio/x-wav" or mime_type == "audio/wav":
        return "wav"
    if mime_type == "audio/webm":
        return "webm"
    if mime_type == "audio/raw":
        return "dat"

    return mime_type

@contextlib.contextmanager
def export_audio_to_wav_ffmpeg(audio: bytearray, mime_type: str) -> str:
    temp_dir = tempfile.gettempdir()

    # Create a temporary file with the appropriate extension
    input_ext = convert_mime_type_to_format(mime_type)
    input_path = os.path.join(temp_dir, f"input_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.{input_ext}")
    with open(input_path, 'wb') as f:
        f.write(audio)

    # Check if the input file exists
    assert os.path.exists(input_path), f"Input file does not exist: {input_path}"

    # Export to wav
    output_path = os.path.join(temp_dir, f"output_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav")
    print(mime_type, input_path, output_path)
    if mime_type == "audio/raw":
        ffmpeg.input(
            input_path,
            f='s16le',
            ar='16000',
            ac=1,
        ).output(output_path).run()
    else:
        ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le', ac=1, ar='16k').run()

    try:
        yield output_path
    finally:
        os.remove(input_path)
        os.remove(output_path)

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr

def get_transcription_file(wav_file_path: str):
    local_path = os.path.join(os.path.dirname(__file__), 'local_service')
    whisper_rust_path = os.path.join(os.path.dirname(__file__), 'whisper-rust', 'target', 'release')
    model_name = os.getenv('WHISPER_MODEL_NAME')
    if not model_name:
        raise EnvironmentError("WHISPER_MODEL_NAME environment variable is not set.")

    output, error = run_command([
        os.path.join(whisper_rust_path, 'whisper-rust'),
        '--model-path', os.path.join(local_path, model_name),
        '--file-path', wav_file_path
    ])

    return output

def get_transcription_bytes(audio_bytes: bytearray, mime_type):
    with export_audio_to_wav_ffmpeg(audio_bytes, mime_type) as wav_file_path:
        return get_transcription_file(wav_file_path)

def stt_bytes(audio_bytes: bytearray, mime_type="audio/wav"):
    with export_audio_to_wav_ffmpeg(audio_bytes, mime_type) as wav_file_path:
        return stt_wav(wav_file_path)

def stt_wav(wav_file_path: str):

    if os.getenv('ALL_LOCAL') == 'False':
        audio_file = open(wav_file_path, "rb")
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
        except openai.BadRequestError as e:
            logger.info(f"openai.BadRequestError: {e}")
            return None

        return transcript
    else:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"output_stt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav")
        ffmpeg.input(wav_file_path).output(output_path, acodec='pcm_s16le', ac=1, ar='16k').run()
        try:
            transcript = get_transcription_file(output_path)
        finally:
            os.remove(output_path)
        return transcript

def stt(input_data, mime_type="audio/wav"):
    if isinstance(input_data, str):
        return stt_wav(input_data)
    elif isinstance(input_data, bytearray):
        return stt_bytes(input_data, mime_type)
    else:
        raise ValueError("Input data should be either a path to a wav file (str) or audio bytes (bytearray)")