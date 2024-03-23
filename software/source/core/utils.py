"""
Core utilty functions for the server and client
"""

import asyncio
import importlib
import os
import platform
from threading import Thread
from typing import NoReturn

from source.server.server import main
from source.server.tunnel import create_tunnel


def get_client_platform(config) -> None:
    """
    Returns the client platform based on the system type.
    """
    if config.client.platform == "auto":
        system_type: str = platform.system()

        # macOS
        if system_type == "Darwin":
            config.client.platform = "mac"

        # Linux
        elif system_type == "Linux":
            try:
                with open("/proc/device-tree/model", "r", encoding="utf-8") as m:
                    if "raspberry pi" in m.read().lower():
                        config.client.platform = "rpi"
                    else:
                        config.client.platform = "linux"
            except FileNotFoundError:
                config.client.platform = "linux"


def handle_exit(signum, frame) -> NoReturn:  # pylint: disable=unused-argument
    """
    Handle exit signal.
    """
    os._exit(0)


def start_client(config) -> Thread:
    """
    Start the client.
    """
    module = importlib.import_module(
        f".clients.{config.client.platform}.device", package="source"
    )

    client_thread = Thread(target=module.main, args=[config.client.url])
    client_thread.start()
    return client_thread


def start_server(config) -> Thread:
    """
    Start the server.
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server_thread = Thread(
        target=loop.run_until_complete,
        args=(
            main(
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
    return server_thread


def start_tunnel(config) -> Thread:
    """
    Start the tunnel.
    """
    tunnel_thread = Thread(
        target=create_tunnel,
        args=[config.tunnel.service, config.server.host, config.server.port],
    )

    tunnel_thread.start()
    return tunnel_thread
