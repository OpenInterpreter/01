# make this obvious
from .profiles.default import interpreter as base_interpreter

# from .profiles.fast import interpreter as base_interpreter
# from .profiles.local import interpreter as base_interpreter

# TODO: remove files i.py, llm.py, conftest?, services

import asyncio
import traceback
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
from uvicorn import Config, Server

# from interpreter import interpreter as base_interpreter
from .async_interpreter import AsyncInterpreter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os


os.environ["STT_RUNNER"] = "server"
os.environ["TTS_RUNNER"] = "server"


async def main(server_host, server_port, tts_service):
    base_interpreter.tts = tts_service
    interpreter = AsyncInterpreter(base_interpreter)

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    @app.get("/ping")
    async def ping():
        return PlainTextResponse("pong")

    @app.post("/load_chat")
    async def load_chat(messages: List[Dict[str, Any]]):
        interpreter.interpreter.messages = messages
        interpreter.active_chat_messages = messages
        print("🪼🪼🪼🪼🪼🪼 Messages loaded: ", interpreter.active_chat_messages)
        return {"status": "success"}

    @app.websocket("/")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:

            async def receive_input():
                while True:
                    if websocket.client_state == "DISCONNECTED":
                        break

                    data = await websocket.receive()

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

                    if isinstance(output, bytes):
                        # print(f"Sending {len(output)} bytes of audio data.")
                        await websocket.send_bytes(output)
                        # we dont send out bytes rn, no TTS

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

    print(f"Starting server on {server_host}:{server_port}")
    config = Config(app, host=server_host, port=server_port, lifespan="on")
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
