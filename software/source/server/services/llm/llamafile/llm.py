import os
import platform
import subprocess
import time
import wget
import stat


class Llm:
    def __init__(self, config):
        self.interpreter = config["interpreter"]
        config.pop("interpreter", None)

        self.install(config["service_directory"])

        config.pop("service_directory", None)
        for key, value in config.items():
            setattr(self.interpreter, key.replace("-", "_"), value)

        self.llm = self.interpreter.llm.completions

    def install(self, service_directory):
        if platform.system() == "Darwin":  # Check if the system is MacOS
            result = subprocess.run(
                ["xcode-select", "-p"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if result.returncode != 0:
                print(
                    "Llamafile requires Mac users to have Xcode installed. You can install Xcode from https://developer.apple.com/xcode/ .\n\nAlternatively, you can use `LM Studio`, `Jan.ai`, or `Ollama` to manage local language models. Learn more at https://docs.openinterpreter.com/guides/running-locally ."
                )
                time.sleep(3)
                raise Exception(
                    "Xcode is not installed. Please install Xcode and try again."
                )

        # Define the path to the models directory
        models_dir = os.path.join(service_directory, "models")

        # Check and create the models directory if it doesn't exist
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        # Define the path to the new llamafile
        llamafile_path = os.path.join(models_dir, "phi-2.Q4_K_M.llamafile")

        # Check if the new llamafile exists, if not download it
        if not os.path.exists(llamafile_path):
            print(
                "Attempting to download the `Phi-2` language model. This may take a few minutes."
            )
            time.sleep(3)

            url = "https://huggingface.co/jartine/phi-2-llamafile/resolve/main/phi-2.Q4_K_M.llamafile"
            wget.download(url, llamafile_path)

        # Make the new llamafile executable
        if platform.system() != "Windows":
            st = os.stat(llamafile_path)
            os.chmod(llamafile_path, st.st_mode | stat.S_IEXEC)

        # Run the new llamafile in the background
        if os.path.exists(llamafile_path):
            try:
                # Test if the llamafile is executable
                subprocess.check_call([f'"{llamafile_path}"'], shell=True)
            except subprocess.CalledProcessError:
                print(
                    "The llamafile is not executable. Please check the file permissions."
                )
                raise
                subprocess.Popen(
                    f'"{llamafile_path}" ' + " ".join(["-ngl", "9999"]), shell=True
                )
        else:
            error_message = "The llamafile does not exist or is corrupted. Please ensure it has been downloaded correctly or try again."
            print(error_message)
            print(error_message)

        self.interpreter.system_message = "You are Open Interpreter, a world-class programmer that can execute code on the user's machine."
        self.interpreter.offline = True

        self.interpreter.llm.model = "local"
        self.interpreter.llm.temperature = 0
        self.interpreter.llm.api_base = "https://localhost:8080/v1"
        self.interpreter.llm.max_tokens = 1000
        self.interpreter.llm.context_window = 3000
        self.interpreter.llm.supports_functions = False
