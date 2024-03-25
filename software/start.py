"""
Application entry point
"""

import asyncio
import importlib
import os
import platform
import signal
import threading

import typer
from source import config
from source.server.utils.local_mode import select_local_model
from source.utils.system import handle_exit

app = typer.Typer()


@app.command()
def start(
    ctx: typer.Context,
    server: bool = typer.Option(False, "--server", help="Run server"),
    server_host: str = typer.Option(
        "0.0.0.0",
        "--server-host",
        help="Specify the server host where the server will deploy",
    ),
    server_port: int = typer.Option(
        10001,
        "--server-port",
        help="Specify the server port where the server will deploy",
    ),
    tunnel_service: str = typer.Option(
        "ngrok", "--tunnel-service", help="Specify the tunnel service"
    ),
    expose: bool = typer.Option(False, "--expose", help="Expose server to internet"),
    client: bool = typer.Option(False, "--client", help="Run client"),
    server_url: str = typer.Option(
        None,
        "--server-url",
        help="Specify the server URL that the client should expect. Defaults to server-host and server-port",
    ),
    client_type: str = typer.Option(
        "auto", "--client-type", help="Specify the client type"
    ),
    llm_service: str = typer.Option(
        "litellm", "--llm-service", help="Specify the LLM service"
    ),
    model: str = typer.Option(None, "--model", help="Specify the model"),
    llm_supports_vision: bool = typer.Option(
        False,
        "--llm-supports-vision",
        help="Specify if the LLM service supports vision",
    ),
    llm_supports_functions: bool = typer.Option(
        False,
        "--llm-supports-functions",
        help="Specify if the LLM service supports functions",
    ),
    context_window: int = typer.Option(
        2048, "--context-window", help="Specify the context window size"
    ),
    max_tokens: int = typer.Option(
        4096, "--max-tokens", help="Specify the maximum number of tokens"
    ),
    temperature: float = typer.Option(
        0.8, "--temperature", help="Specify the temperature for generation"
    ),
    tts_service: str = typer.Option(
        "openai", "--tts-service", help="Specify the TTS service"
    ),
    stt_service: str = typer.Option(
        "openai", "--stt-service", help="Specify the STT service"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use recommended local services for LLM, STT, and TTS"
    ),
) -> None:
    """
    Setup the application.
    """
    signal.signal(signal.SIGINT, handle_exit)
    config.apply_cli_args(ctx.params)

    if config.local.enabled:
        config.tts.service = "piper"
        config.stt.service = "local-whisper"

        if not model:
            select_local_model()

    if not server_url:
        server_url = f"{config.server.host}:{config.server.port}"

    if not config.server.enabled and not config.client.enabled:
        config.server.enabled = True
        config.client.enabled = True

    # Temporary fix pending refactor of `server` and `tunnel` modules.
    # Prevents early execution of top-level code until config is fully initialized.
    server_module = importlib.import_module("source.server.server")
    tunnel_module = importlib.import_module("source.server.tunnel")

    if config.server.enabled:
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server_thread = threading.Thread(
            target=loop.run_until_complete,
            args=(
                server_module.main(
                    config.server.host,
                    config.server.port,
                    config.llm.service,
                    config.llm.model,
                    config.llm.vision_enabled,
                    config.llm.functions_enabled,
                    config.llm.context_window,
                    config.llm.max_tokens,
                    config.llm.temperature,
                    config.tts.service,
                    config.stt.service,
                ),
            ),
        )
        server_thread.start()

    if config.tunnel.exposed:
        tunnel_thread = threading.Thread(
            target=tunnel_module.create_tunnel,
            args=[config.tunnel.service, config.server.host, config.server.port],
        )
        tunnel_thread.start()

    if config.client.enabled:
        if config.client.platform == "auto":
            system: str = platform.system()
            if system == "Darwin":  # macOS
                config.client.platform = "mac"
            elif system == "Linux":
                try:
                    with open("/proc/device-tree/model", "r", encoding="utf-8") as m:
                        if "raspberry pi" in m.read().lower():
                            config.client.platform = "rpi"
                        else:
                            config.client.platform = "linux"
                except FileNotFoundError:
                    config.client.platform = "linux"

        module = importlib.import_module(
            f".clients.{config.client.platform}.device", package="source"
        )
        client_thread = threading.Thread(target=module.main, args=[server_url])
        client_thread.start()

    try:
        if config.server.enabled:
            server_thread.join()
        if config.tunnel.exposed:
            tunnel_thread.join()
        if config.client.enabled:
            client_thread.join()
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGINT)
