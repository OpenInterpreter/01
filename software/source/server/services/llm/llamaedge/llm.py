import os
import subprocess
import requests
import json


class Llm:
    def __init__(self, config):
        self.install(config["service_directory"])

    def install(self, service_directory):
        LLM_FOLDER_PATH = service_directory
        self.llm_directory = os.path.join(LLM_FOLDER_PATH, "llm")
        if not os.path.isdir(self.llm_directory):  # Check if the LLM directory exists
            os.makedirs(LLM_FOLDER_PATH, exist_ok=True)

            # Install WasmEdge
            subprocess.run(
                [
                    "curl",
                    "-sSf",
                    "https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install.sh",
                    "|",
                    "bash",
                    "-s",
                    "--",
                    "--plugin",
                    "wasi_nn-ggml",
                ]
            )

            # Download the Qwen1.5-0.5B-Chat model GGUF file
            MODEL_URL = "https://huggingface.co/second-state/Qwen1.5-0.5B-Chat-GGUF/resolve/main/Qwen1.5-0.5B-Chat-Q5_K_M.gguf"
            subprocess.run(["curl", "-LO", MODEL_URL], cwd=self.llm_directory)

            # Download the llama-api-server.wasm app
            APP_URL = "https://github.com/LlamaEdge/LlamaEdge/releases/latest/download/llama-api-server.wasm"
            subprocess.run(["curl", "-LO", APP_URL], cwd=self.llm_directory)

            # Run the API server
            subprocess.run(
                [
                    "wasmedge",
                    "--dir",
                    ".:.",
                    "--nn-preload",
                    "default:GGML:AUTO:Qwen1.5-0.5B-Chat-Q5_K_M.gguf",
                    "llama-api-server.wasm",
                    "-p",
                    "llama-2-chat",
                ],
                cwd=self.llm_directory,
            )

            print("LLM setup completed.")
        else:
            print("LLM already set up. Skipping download.")

    def llm(self, messages):
        url = "http://localhost:8080/v1/chat/completions"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"messages": messages, "model": "llama-2-chat"}
        with requests.post(
            url, headers=headers, data=json.dumps(data), stream=True
        ) as response:
            for line in response.iter_lines():
                if line:
                    yield json.loads(line)
