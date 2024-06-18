import typer
import asyncio
import platform
import threading
import os
import importlib
from source.server.tunnel import create_tunnel
from source.server.async_server import main

import signal

app = typer.Typer()


@app.command()
def run(
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
    qr: bool = typer.Option(
        False, "--qr", help="Display QR code to scan to connect to the server"
    ),
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
        qr=qr,
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
    qr: bool = False,
):

    system_type = platform.system()
    if system_type == "Windows":
        server_host = "localhost"

    if not server_url:
        server_url = f"{server_host}:{server_port}"

    if not server and not client:
        server = True
        client = True

    def handle_exit(signum, frame):
        os._exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    if server:
        # print(f"Starting server with mobile = {mobile}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server_thread = threading.Thread(
            target=loop.run_until_complete,
            args=(
                main(
                    server_host,
                    server_port,
                ),
            ),
        )
        server_thread.start()

    if expose:
        tunnel_thread = threading.Thread(
            target=create_tunnel, args=[tunnel_service, server_host, server_port, qr]
        )
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
                    with open("/proc/device-tree/model", "r") as m:
                        if "raspberry pi" in m.read().lower():
                            client_type = "rpi"
                        else:
                            client_type = "linux"
                except FileNotFoundError:
                    client_type = "linux"

        module = importlib.import_module(
            f".clients.{client_type}.device", package="source"
        )

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
