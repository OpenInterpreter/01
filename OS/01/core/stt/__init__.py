from datetime import datetime
import os
import contextlib
import tempfile
import ffmpeg
import subprocess

def convert_mime_type_to_format(mime_type: str) -> str:
    if mime_type == "audio/x-wav":
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
        #os.remove(output_path)

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr

def get_transcription(audio_bytes: bytearray, mime_type):
    with export_audio_to_wav_ffmpeg(audio_bytes, mime_type) as wav_file_path:
        model_path = os.getenv("WHISPER_MODEL_PATH")
        if not model_path:
            raise EnvironmentError("WHISPER_MODEL_PATH environment variable is not set.")

        output, error = run_command([
            os.path.join(os.path.dirname(__file__), 'whisper-rust', 'target', 'release', 'whisper-rust'),
            '--model-path', model_path,
            '--file-path', wav_file_path
        ])

        print("Exciting transcription result:", output)
        return output