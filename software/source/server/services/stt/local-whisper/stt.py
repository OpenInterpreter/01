"""
Defines a function which takes a path to an audio file and turns it into text.
"""

from datetime import datetime
import os
import contextlib
import platform
import tempfile
import shutil
import ffmpeg
import subprocess
import urllib.request


class Stt:
    def __init__(self, config):
        self.service_directory = config["service_directory"]
        install(self.service_directory)

    def stt(self, audio_file_path):
        return stt(self.service_directory, audio_file_path)


def install(service_dir):
    ### INSTALL

    WHISPER_RUST_PATH = os.path.join(service_dir, "whisper-rust")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    source_whisper_rust_path = os.path.join(script_dir, "whisper-rust")
    if not os.path.exists(source_whisper_rust_path):
        print(f"Source directory does not exist: {source_whisper_rust_path}")
        exit(1)
    if not os.path.exists(WHISPER_RUST_PATH):
        shutil.copytree(source_whisper_rust_path, WHISPER_RUST_PATH)

    os.chdir(WHISPER_RUST_PATH)

    # Check if whisper-rust executable exists before attempting to build
    if not os.path.isfile(
        os.path.join(WHISPER_RUST_PATH, "target/release/whisper-rust")
    ):
        # Check if Rust is installed. Needed to build whisper executable

        rustc_path = shutil.which("rustc")

        if rustc_path is None:
            print(
                "Rust is not installed or is not in system PATH. Please install Rust before proceeding."
            )
            exit(1)

        # Build Whisper Rust executable if not found
        subprocess.run(["cargo", "build", "--release"], check=True)
    else:
        print("Whisper Rust executable already exists. Skipping build.")

    WHISPER_MODEL_PATH = os.path.join(service_dir, "model")
    WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "ggml-tiny.en.bin")
    while not valid_model(WHISPER_MODEL_PATH, WHISPER_MODEL_NAME):
        print(f"Downloading Whisper model '{WHISPER_MODEL_NAME}'.")
        WHISPER_MODEL_URL = os.getenv(
            "WHISPER_MODEL_URL",
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/",
        )
        os.makedirs(WHISPER_MODEL_PATH, exist_ok=True)
        urllib.request.urlretrieve(
            f"{WHISPER_MODEL_URL}{WHISPER_MODEL_NAME}",
            os.path.join(WHISPER_MODEL_PATH, WHISPER_MODEL_NAME),
        )
    else:
        print(f"Whisper model '{WHISPER_MODEL_NAME}' installed.")


def valid_model(model_path: str, model_file: str) -> bool:
    # Try to validate model through cryptographic hash comparison

    model_file_path = os.path.join(model_path, model_file)
    if not os.path.isfile(model_file_path):
        return False

    # Download details file and get hash
    details_file = f"https://huggingface.co/ggerganov/whisper.cpp/raw/main/{model_file}"
    try:
        with urllib.request.urlopen(details_file) as response:
            body_bytes = response.read()
    except:
        print("Internet connection not detected. Skipping validation.")
        return True

    lines = body_bytes.splitlines()
    colon_index = lines[1].find(b':')
    details_hash = lines[1][colon_index + 1:].decode()

    # Generate model hash using native commands
    model_hash = None
    system = platform.system()
    if system == 'Darwin':
        shasum_path = shutil.which('shasum')
        model_hash = subprocess.check_output(
            f"{shasum_path} -a 256 {model_file_path} | cut -d' ' -f1",
            text=True,
            shell=True
        )
    elif system == 'Linux':
        sha256sum_path = shutil.which('sha256sum')
        model_hash = subprocess.check_output(
            f"{sha256sum_path} {model_file_path} | cut -d' ' -f1",
            text=True,
            shell=True
        )
    elif system == 'Windows':
        comspec = os.getenv("COMSPEC")
        if comspec.endswith('cmd.exe'): # Most likely
            certutil_path = shutil.which('certutil')
            first_op = f"{certutil_path} -hashfile {model_file_path} sha256"
            second_op = 'findstr /v "SHA256 CertUtil"' # Prints only lines that do not contain a match.
            model_hash = subprocess.check_output(f"{first_op} | {second_op}", text=True, shell=True)
        else:
            first_op = f"Get-FileHash -LiteralPath {model_file_path} -Algorithm SHA256"
            subsequent_ops = "Select-Object Hash | Format-Table -HideTableHeaders | Out-String"
            model_hash = subprocess.check_output([
                'pwsh',
                '-Command',
                f"({first_op} | {subsequent_ops}).trim().toLower()"
                ],
                text=True
            )
    else:
        print(f"System '{system}' not supported. Skipping validation.")
        return True

    if details_hash == model_hash.strip():
        print(f"Whisper model '{model_file}' file is valid.")
    else:
        msg = f'''
            The model '{model_file}' did not validate. STT may not function correctly.
            The model path is '{model_path}'.
            Manually download and verify the model's hash to get better functionality.
            Continuing.
        '''
        print(msg)

    return True


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
    input_path = os.path.join(
        temp_dir, f"input_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.{input_ext}"
    )
    with open(input_path, "wb") as f:
        f.write(audio)

    # Check if the input file exists
    assert os.path.exists(input_path), f"Input file does not exist: {input_path}"

    # Export to wav
    output_path = os.path.join(
        temp_dir, f"output_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav"
    )
    print(mime_type, input_path, output_path)
    if mime_type == "audio/raw":
        ffmpeg.input(
            input_path,
            f="s16le",
            ar="16000",
            ac=1,
        ).output(output_path, loglevel="panic").run()
    else:
        ffmpeg.input(input_path).output(
            output_path, acodec="pcm_s16le", ac=1, ar="16k", loglevel="panic"
        ).run()

    try:
        yield output_path
    finally:
        os.remove(input_path)
        os.remove(output_path)


def run_command(command):
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    return result.stdout, result.stderr


def get_transcription_file(service_directory, wav_file_path: str):
    local_path = os.path.join(service_directory, "model")
    whisper_rust_path = os.path.join(
        service_directory, "whisper-rust", "target", "release"
    )
    model_name = os.getenv("WHISPER_MODEL_NAME", "ggml-tiny.en.bin")

    output, _ = run_command(
        [
            os.path.join(whisper_rust_path, "whisper-rust"),
            "--model-path",
            os.path.join(local_path, model_name),
            "--file-path",
            wav_file_path,
        ]
    )

    return output


def stt_wav(service_directory, wav_file_path: str):
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(
        temp_dir, f"output_stt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav"
    )
    ffmpeg.input(wav_file_path).output(
        output_path, acodec="pcm_s16le", ac=1, ar="16k", loglevel="panic"
    ).run()
    try:
        transcript = get_transcription_file(service_directory, output_path)
    finally:
        os.remove(output_path)
    return transcript


def stt(service_directory, input_data):
    return stt_wav(service_directory, input_data)
