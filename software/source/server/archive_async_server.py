import asyncio
import traceback
import json
from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import PlainTextResponse
from uvicorn import Config, Server
from .async_interpreter import AsyncInterpreter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import importlib.util



os.environ["STT_RUNNER"] = "server"
os.environ["TTS_RUNNER"] = "server"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


async def get_debug_flag():
    return app.state.debug


@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")


@app.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket, debug: bool = Depends(get_debug_flag)
):
    await websocket.accept()

    global global_interpreter
    interpreter = global_interpreter

    # Send the tts_service value to the client
    await websocket.send_text(
        json.dumps({"type": "config", "tts_service": interpreter.interpreter.tts})
    )

    try:

        async def receive_input():
            while True:
                if websocket.client_state == "DISCONNECTED":
                    break

                data = await websocket.receive()

                await asyncio.sleep(0)

                if isinstance(data, bytes):
                    await interpreter.input(data)
                elif "bytes" in data:
                    await interpreter.input(data["bytes"])
                    # print("RECEIVED INPUT", data)
                elif "text" in data:
                    # print("RECEIVED INPUT", data)
                    await interpreter.input(data["text"])

        async def send_output():
            while True:
                output = await interpreter.output()

                await asyncio.sleep(0)

                if isinstance(output, bytes):
                    # print(f"Sending {len(output)} bytes of audio data.")
                    await websocket.send_bytes(output)

                elif isinstance(output, dict):
                    # print("sending text")
                    await websocket.send_text(json.dumps(output))

        await asyncio.gather(send_output(), receive_input())
    except Exception as e:
        print(f"WebSocket connection closed with exception: {e}")
        traceback.print_exc()
    finally:
        if not websocket.client_state == "DISCONNECTED":
            await websocket.close()


async def main(server_host, server_port, profile, debug):

    app.state.debug = debug

    # Load the profile module from the provided path
    spec = importlib.util.spec_from_file_location("profile", profile)
    profile_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile_module)

    # Get the interpreter from the profile
    interpreter = profile_module.interpreter

    if not hasattr(interpreter, 'tts'):
        print("Setting TTS provider to default: openai")
        interpreter.tts = "openai"

    # Make it async
    interpreter = AsyncInterpreter(interpreter, debug)

    global global_interpreter
    global_interpreter = interpreter

    print(f"Starting server on {server_host}:{server_port}")
    config = Config(app, host=server_host, port=server_port, lifespan="on")
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
