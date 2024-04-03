import ffmpeg
import tempfile
import os
import subprocess
import urllib.request
import tarfile
import platform


class Tts:
    def __init__(self, config):
        self.piper_directory = ""
        self.install(config["service_directory"])

    def tts(self, text):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_file = temp_file.name
            piper_dir = self.piper_directory
            subprocess.run(
                [
                    os.path.join(piper_dir, "piper"),
                    "--model",
                    os.path.join(
                        piper_dir,
                        os.getenv("PIPER_VOICE_NAME", "en_US-lessac-medium.onnx"),
                    ),
                    "--output_file",
                    output_file,
                ],
                input=text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # TODO: hack to format audio correctly for device
            outfile = tempfile.gettempdir() + "/" + "raw.dat"
            ffmpeg.input(temp_file.name).output(
                outfile, f="s16le", ar="16000", ac="1", loglevel="panic"
            ).run()

            return outfile

    def install(self, service_directory):
        PIPER_FOLDER_PATH = service_directory
        self.piper_directory = os.path.join(PIPER_FOLDER_PATH, "piper")
        if not os.path.isdir(
            self.piper_directory
        ):  # Check if the Piper directory exists
            os.makedirs(PIPER_FOLDER_PATH, exist_ok=True)

            # Determine OS and architecture
            OS = platform.system().lower()
            ARCH = platform.machine()
            if OS == "darwin":
                OS = "macos"
                if ARCH == "arm64":
                    ARCH = "aarch64"
                elif ARCH == "x86_64":
                    ARCH = "x64"
                else:
                    print("Piper: unsupported architecture")
                    return
            elif OS == "windows":
                if ARCH == "AMD64":
                    ARCH = "amd64"
                else:
                    print("Piper: unsupported architecture")
                    return

            PIPER_ASSETNAME = f"piper_{OS}_{ARCH}.tar.gz"
            PIPER_URL = "https://github.com/rhasspy/piper/releases/latest/download/"

            asset_url = f"{PIPER_URL}{PIPER_ASSETNAME}"

            if OS == "windows":
                asset_url = asset_url.replace(".tar.gz", ".zip")

            # Download and extract Piper
            urllib.request.urlretrieve(
                asset_url, os.path.join(PIPER_FOLDER_PATH, PIPER_ASSETNAME)
            )

            # Extract the downloaded file
            if OS == "windows":
                import zipfile

                with zipfile.ZipFile(
                    os.path.join(PIPER_FOLDER_PATH, PIPER_ASSETNAME), "r"
                ) as zip_ref:
                    zip_ref.extractall(path=PIPER_FOLDER_PATH)
            else:
                with tarfile.open(
                    os.path.join(PIPER_FOLDER_PATH, PIPER_ASSETNAME), "r:gz"
                ) as tar:
                    tar.extractall(path=PIPER_FOLDER_PATH)

            PIPER_VOICE_URL = os.getenv(
                "PIPER_VOICE_URL",
                "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/",
            )
            PIPER_VOICE_NAME = os.getenv("PIPER_VOICE_NAME", "en_US-lessac-medium.onnx")

            # Download voice model and its json file
            urllib.request.urlretrieve(
                f"{PIPER_VOICE_URL}{PIPER_VOICE_NAME}",
                os.path.join(self.piper_directory, PIPER_VOICE_NAME),
            )
            urllib.request.urlretrieve(
                f"{PIPER_VOICE_URL}{PIPER_VOICE_NAME}.json",
                os.path.join(self.piper_directory, f"{PIPER_VOICE_NAME}.json"),
            )

            # Additional setup for macOS
            if OS == "macos":
                if ARCH == "x64":
                    subprocess.run(
                        ["softwareupdate", "--install-rosetta", "--agree-to-license"]
                    )

                PIPER_PHONEMIZE_ASSETNAME = f"piper-phonemize_{OS}_{ARCH}.tar.gz"
                PIPER_PHONEMIZE_URL = "https://github.com/rhasspy/piper-phonemize/releases/latest/download/"
                urllib.request.urlretrieve(
                    f"{PIPER_PHONEMIZE_URL}{PIPER_PHONEMIZE_ASSETNAME}",
                    os.path.join(self.piper_directory, PIPER_PHONEMIZE_ASSETNAME),
                )

                with tarfile.open(
                    os.path.join(self.piper_directory, PIPER_PHONEMIZE_ASSETNAME),
                    "r:gz",
                ) as tar:
                    tar.extractall(path=self.piper_directory)

                PIPER_DIR = self.piper_directory
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libespeak-ng.1.dylib",
                        f"{PIPER_DIR}/piper-phonemize/lib/libespeak-ng.1.dylib",
                        f"{PIPER_DIR}/piper",
                    ]
                )
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libonnxruntime.1.14.1.dylib",
                        f"{PIPER_DIR}/piper-phonemize/lib/libonnxruntime.1.14.1.dylib",
                        f"{PIPER_DIR}/piper",
                    ]
                )
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libpiper_phonemize.1.dylib",
                        f"{PIPER_DIR}/piper-phonemize/lib/libpiper_phonemize.1.dylib",
                        f"{PIPER_DIR}/piper",
                    ]
                )

            print("Piper setup completed.")
        else:
            print("Piper already set up. Skipping download.")
