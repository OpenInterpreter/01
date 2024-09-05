from yaspin import yaspin
spinner = yaspin()
spinner.start()

import typer
import ngrok
import platform
import threading
import os
import importlib
from source.server.server import start_server
import subprocess
import webview
import socket
import json
import segno
from livekit import api
import time
from dotenv import load_dotenv
import signal
from source.server.livekit.worker import main as worker_main
import warnings
import requests

load_dotenv()

system_type = platform.system()

app = typer.Typer()

@app.command()
def run(
    server: str = typer.Option(
        None,
        "--server",
        help="Run server (accepts `livekit` or `light`)",
    ),
    server_host: str = typer.Option(
        "0.0.0.0",
        "--server-host",
        help="Specify the server host where the server will deploy",
    ),
    server_port: int = typer.Option(
        10101,
        "--server-port",
        help="Specify the server port where the server will deploy",
    ),
    expose: bool = typer.Option(False, "--expose", help="Expose server over the internet"),
    domain: str = typer.Option(None, "--domain", help="Use `--expose` with a custom ngrok domain"),
    client: str = typer.Option(None, "--client", help="Run client of a particular type. Accepts `light-python`, defaults to `light-python`"),
    server_url: str = typer.Option(
        None,
        "--server-url",
        help="Specify the server URL that the --client should expect. Defaults to server-host and server-port",
    ),
    qr: bool = typer.Option(
        False, "--qr", help="Display QR code containing the server connection information (will be ngrok url if `--expose` is used)"
    ),
    profiles: bool = typer.Option(
        False,
        "--profiles",
        help="Opens the folder where profiles are contained",
    ),
    profile: str = typer.Option(
        "default.py",
        "--profile",
        help="Specify the path to the profile, or the name of the file if it's in the `profiles` directory (run `--profiles` to open the profiles directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Print latency measurements and save microphone recordings locally for manual playback",
    ),
):

    threads = []

    # Handle `01` with no arguments, which should start server + client
    if not server and not client:
        server = "light"
        client = "light-python"

    ### PROFILES

    profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "source", "server", "profiles")

    if profiles:
        if platform.system() == "Windows":
            subprocess.Popen(['explorer', profiles_dir])
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', profiles_dir])
        elif platform.system() == "Linux":
            subprocess.Popen(['xdg-open', profiles_dir])
        else:
            subprocess.Popen(['open', profiles_dir])
        exit(0)

    if profile:
        if not os.path.isfile(profile):
            profile = os.path.join(profiles_dir, profile)
            if not os.path.isfile(profile):
                profile += ".py"
                if not os.path.isfile(profile):
                    print(f"Invalid profile path: {profile}")
                    exit(1)


    ### SERVER

    if system_type == "Windows":
        server_host = "localhost"

    if not server_url:
        server_url = f"{server_host}:{server_port}"

    if server:

        ### LIGHT SERVER (required by livekit)

        if server == "light":
            light_server_port = server_port
            light_server_host = server_host
            voice = True # The light server will support voice
        elif server == "livekit":
            # The light server should run at a different port if we want to run a livekit server
            spinner.stop()
            print(f"Starting light server (required for livekit server) on localhost, on the port before `--server-port` (port {server_port-1}), unless the `AN_OPEN_PORT` env var is set.")
            print(f"The livekit server will be started on port {server_port}.")
            light_server_port = os.getenv('AN_OPEN_PORT', server_port-1)
            light_server_host = "localhost"
            voice = False # The light server will NOT support voice. It will just run Open Interpreter. The Livekit server will handle voice

        server_thread = threading.Thread(
            target=start_server,
            args=(
                light_server_host,
                light_server_port,
                profile,
                voice,
                debug
            ),
        )
        spinner.stop()
        print("Starting server...")
        server_thread.start()
        threads.append(server_thread)

        if server == "livekit":

            ### LIVEKIT SERVER

            def run_command(command):
                subprocess.run(command, shell=True, check=True)

            # Start the livekit server
            if debug:
                command = f'livekit-server --dev --bind "{server_host}" --port {server_port}'
            else:
                command = f'livekit-server --dev --bind "{server_host}" --port {server_port} > /dev/null 2>&1'
            livekit_thread = threading.Thread(
                target=run_command, args=(command,)
            )
            time.sleep(7)
            livekit_thread.start()
            threads.append(livekit_thread)

            local_livekit_url = f"ws://{server_host}:{server_port}"

        if expose:

            ### EXPOSE OVER INTERNET
            listener = ngrok.forward(f"{server_host}:{server_port}", authtoken_from_env=True, domain=domain)
            url = listener.url()

        else:

            ### GET LOCAL URL
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            url = f"http://{ip_address}:{server_port}"


        if server == "livekit":
            print("Livekit server will run at:", url)


    ### CLIENT

    if client:
        
        module = importlib.import_module(
            f".clients.{client}.client", package="source"
        )

        client_thread = threading.Thread(target=module.run, args=[server_url, debug])
        spinner.stop()
        print("Starting client...")
        client_thread.start()
        threads.append(client_thread)


    ### WAIT FOR THREADS TO FINISH, HANDLE CTRL-C

    # Signal handler for termination signals
    def signal_handler(sig, frame):
        print("Termination signal received. Shutting down...")
        for thread in threads:
            if thread.is_alive():
                # Kill subprocess associated with thread
                subprocess.run(f"pkill -P {os.getpid()}", shell=True)
        os._exit(0)

    # Register signal handler for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:

        # Verify the server is running
        for attempt in range(10):
            try:
                response = requests.get(url)
                status = "OK" if response.status_code == 200 else "Not OK"
                if status == "OK":
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            raise Exception(f"Server at {url} failed to respond after 10 attempts")

        ### DISPLAY QR CODE
        if qr:
            def display_qr_code():
                time.sleep(10)
                content = json.dumps({"livekit_server": url})
                qr_code = segno.make(content)
                qr_code.terminal(compact=True)

            qr_thread = threading.Thread(target=display_qr_code)
            qr_thread.start()
            threads.append(qr_thread)

        ### START LIVEKIT WORKER
        if server == "livekit":
            time.sleep(7)
            # These are needed to communicate with the worker's entrypoint
            os.environ['INTERPRETER_SERVER_HOST'] = light_server_host
            os.environ['INTERPRETER_SERVER_PORT'] = str(light_server_port)

            token = str(api.AccessToken('devkey', 'secret') \
                .with_identity("identity") \
                .with_name("my name") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room="my-room",
            )).to_jwt())

            meet_url = f'https://meet.livekit.io/custom?liveKitUrl={url.replace("http", "ws")}&token={token}\n\n'
            print(meet_url)

            for attempt in range(30):
                try:
                    worker_main(local_livekit_url)
                except KeyboardInterrupt:
                    print("Exiting.")
                    raise
                except Exception as e:
                    print(f"Error occurred: {e}")
                print("Retrying...")
                time.sleep(1)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        # On KeyboardInterrupt, send SIGINT to self
        os.kill(os.getpid(), signal.SIGINT)