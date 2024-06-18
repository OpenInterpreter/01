import asyncio
import traceback
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
from uvicorn import Config, Server
from .i import configure_interpreter
from interpreter import interpreter as base_interpreter
from starlette.websockets import WebSocketDisconnect
from .async_interpreter import AsyncInterpreter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os


os.environ["STT_RUNNER"] = "server"
os.environ["TTS_RUNNER"] = "server"


async def main(server_host, server_port, tts_service, asynchronous):
    if asynchronous:
        base_interpreter.system_message = (
            "You are a helpful assistant that can answer questions and help with tasks."
        )
        base_interpreter.computer.import_computer_api = False
        base_interpreter.llm.model = "groq/llama3-8b-8192"
        base_interpreter.llm.api_key = os.environ["GROQ_API_KEY"]
        base_interpreter.llm.supports_functions = False
        base_interpreter.auto_run = True
        base_interpreter.tts = tts_service
        interpreter = AsyncInterpreter(base_interpreter)
    else:
        configured_interpreter = configure_interpreter(base_interpreter)
        configured_interpreter.llm.supports_functions = True
        configured_interpreter.tts = tts_service
        interpreter = AsyncInterpreter(configured_interpreter)

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

    print("About to set up the websocker endpoint!!!!!!!!!!!!!!!!!!!!!!!!!")

    @app.websocket("/")
    async def websocket_endpoint(websocket: WebSocket):
        print("websocket hit")
        await websocket.accept()
        print("websocket accepted")

        async def send_output():
            try:
                while True:
                    output = await interpreter.output()

                    if isinstance(output, bytes):
                        print("server sending bytes output")
                        try:
                            await websocket.send_bytes(output)
                            print("server successfully sent bytes output")
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                            return {"error": str(e)}

                    elif isinstance(output, dict):
                        print("server sending text output")
                        try:
                            await websocket.send_text(json.dumps(output))
                            print("server successfully sent text output")
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                            return {"error": str(e)}
            except asyncio.CancelledError:
                print("WebSocket connection closed")
                traceback.print_exc()

        async def receive_input():
            try:
                while True:
                    # print("server awaiting input")
                    data = await websocket.receive()

                    if isinstance(data, bytes):
                        try:
                            await interpreter.input(data)
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                            return {"error": str(e)}

                    elif "bytes" in data:
                        try:
                            await interpreter.input(data["bytes"])
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                            return {"error": str(e)}

                    elif "text" in data:
                        try:
                            await interpreter.input(data["text"])
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                            return {"error": str(e)}
            except asyncio.CancelledError:
                print("WebSocket connection closed")
                traceback.print_exc()

        try:
            send_task = asyncio.create_task(send_output())
            receive_task = asyncio.create_task(receive_input())

            print("server starting to handle ws connection")
            """
            done, pending = await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            for task in done:
                if task.exception() is not None:
                    raise
            """
            await asyncio.gather(send_task, receive_task)

            print("server finished handling ws connection")

        except WebSocketDisconnect:
            print("WebSocket disconnected")
        except Exception as e:
            print(f"WebSocket connection closed with exception: {e}")
            traceback.print_exc()
        finally:
            print("server closing ws connection")
            await websocket.close()

    print(f"Starting server on {server_host}:{server_port}")
    config = Config(app, host=server_host, port=server_port, lifespan="on")
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main("localhost", 8000))
