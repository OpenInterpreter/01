import typer
import asyncio
import platform
import concurrent.futures
import threading
import os
import importlib
from source.server.tunnel import create_tunnel
from source.server.server import main
from source.server.utils.local_mode import select_local_model

import signal
app = typer.Typer()

@app.command()
def run(
            server: bool = typer.Option(False, "--server", help="Run server"),
            server_host: str = typer.Option("0.0.0.0", "--server-host", help="Specify the server host where the server will deploy"),
            server_port: int = typer.Option(10001, "--server-port", help="Specify the server port where the server will deploy"),
            
            tunnel_service: str = typer.Option("ngrok", "--tunnel-service", help="Specify the tunnel service"),
            expose: bool = typer.Option(False, "--expose", help="Expose server to internet"),
            
            client: bool = typer.Option(False, "--client", help="Run client"),
            server_url: str = typer.Option(None, "--server-url", help="Specify the server URL that the client should expect. Defaults to server-host and server-port"),
            client_type: str = typer.Option("auto", "--client-type", help="Specify the client type"),
            
            llm_service: str = typer.Option("litellm", "--llm-service", help="Specify the LLM service"),
            
            model: str = typer.Option("gpt-4", "--model", help="Specify the model"),
            llm_supports_vision: bool = typer.Option(False, "--llm-supports-vision", help="Specify if the LLM service supports vision"),
            llm_supports_functions: bool = typer.Option(False, "--llm-supports-functions", help="Specify if the LLM service supports functions"),
            context_window: int = typer.Option(2048, "--context-window", help="Specify the context window size"),
            max_tokens: int = typer.Option(4096, "--max-tokens", help="Specify the maximum number of tokens"),
            temperature: float = typer.Option(0.8, "--temperature", help="Specify the temperature for generation"),
            
            tts_service: str = typer.Option("openai", "--tts-service", help="Specify the TTS service"),
            
            stt_service: str = typer.Option("openai", "--stt-service", help="Specify the STT service"),

            local: bool = typer.Option(False, "--local", help="Use recommended local services for LLM, STT, and TTS"),
            
            qr: bool = typer.Option(False, "--qr", help="Print the QR code for the server URL")
        ):
    
    _run(
        server=server,
        server_host=server_host,
        server_port=server_port,
        tunnel_service=tunnel_service,
        expose=expose,
        client=client,
        server_url=server_url,
        client_type=client_type,
        llm_service=llm_service,
        model=model,
        llm_supports_vision=llm_supports_vision,
        llm_supports_functions=llm_supports_functions,
        context_window=context_window,
        max_tokens=max_tokens,
        temperature=temperature,
        tts_service=tts_service,
        stt_service=stt_service,
        local=local,
        qr=qr
    )

def _run(
            server: bool = False,
            server_host: str = "0.0.0.0",
            server_port: int = 10001,
            
            tunnel_service: str = "bore",
            expose: bool = False,
            
            client: bool = False,
            server_url: str = None,
            client_type: str = "auto",
            
            llm_service: str = "litellm",
            
            model: str = "gpt-4",
            llm_supports_vision: bool = False,
            llm_supports_functions: bool = False,
            context_window: int = 2048,
            max_tokens: int = 4096,
            temperature: float = 0.8,
            
            tts_service: str = "openai",
            
            stt_service: str = "openai",

            local: bool = False,
            
            qr: bool = False
        ):
    
    if local:
        tts_service = "piper"
        # llm_service = "llamafile"
        stt_service = "local-whisper"
        select_local_model()
    
    if not server_url:
        server_url = f"{server_host}:{server_port}"
    
    if not server and not client:
        server = True
        client = True

    def handle_exit(signum, frame):
        os._exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    if server:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server_thread = threading.Thread(target=loop.run_until_complete, args=(main(server_host, server_port, llm_service, model, llm_supports_vision, llm_supports_functions, context_window, max_tokens, temperature, tts_service, stt_service),))
        server_thread.start()

    if expose:
        tunnel_thread = threading.Thread(target=create_tunnel, args=[tunnel_service, server_host, server_port, qr])
        tunnel_thread.start()

    if client:
        if client_type == "auto":
            system_type = platform.system()
            if system_type == "Darwin":  # Mac OS
                client_type = "mac"
            elif system_type == "Windows":  # Windows System
                client_type = "windows"
            elif system_type == "Linux":  # Linux System
                try:
                    with open('/proc/device-tree/model', 'r') as m:
                        if 'raspberry pi' in m.read().lower():
                            client_type = "rpi"
                        else:
                            client_type = "linux"
                except FileNotFoundError:
                    client_type = "linux"

        module = importlib.import_module(f".clients.{client_type}.device", package='source')
        client_thread = threading.Thread(target=module.main, args=[server_url])
        client_thread.start()

    try:
        if server:
            server_thread.join()
        if expose:
            tunnel_thread.join()
        if client:
            client_thread.join()
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGINT)