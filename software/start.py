"""
Application entry point
"""

import signal
from threading import Thread

from source import config
from source.core.utils import (
    get_client_platform,
    handle_exit,
    start_client,
    start_server,
    start_tunnel,
)
from source.server.utils.local_mode import select_local_model


def run() -> None:
    """
    Run the application.
    """
    # Set up signal handler for SIGINT (keyboard interrupt)
    signal.signal(signal.SIGINT, handle_exit)

    # If platform is set to auto, determine user's platform automatically.
    if config.client.platform == "auto":
        get_client_platform(config)

    # If local mode is enabled, set up local services
    if config.local.enabled:
        config.tts.service = config.local.tts_service
        config.stt.service = config.local.stt_service
        select_local_model()

    # If no client URL is provided, set one using server host and port.
    config.client.url = (
        config.client.url or f"{config.server.host}:{config.server.port}"
    )

    if not config.server.enabled and not config.client.enabled:
        config.server.enabled = config.client.enabled = True

    server_thread: Thread | None = (
        start_server(config) if config.server.enabled else None
    )

    tunnel_thread: Thread | None = (
        start_tunnel(config) if config.tunnel.exposed else None
    )

    client_thread: Thread | None = (
        start_client(config) if config.client.enabled else None
    )

    try:
        if server_thread:
            server_thread.join()
        if tunnel_thread:
            tunnel_thread.join()
        if client_thread and client_thread.is_alive():
            client_thread.join()
    except KeyboardInterrupt:
        handle_exit(signal.SIGINT, None)


if __name__ == "__main__":
    run()
