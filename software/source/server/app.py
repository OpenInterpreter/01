from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio
from .utils.logs import setup_logging
from .utils.logs import logger
import traceback
import json
from ..utils.print_markdown import print_markdown
from .queues import Queues


setup_logging()

app = FastAPI()

from_computer, from_user, to_device = Queues.get()


@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    receive_task = asyncio.create_task(receive_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket))
    try:
        await asyncio.gather(receive_task, send_task)
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.info(f"Connection lost. Error: {e}")


@app.post("/")
async def add_computer_message(request: Request):
    body = await request.json()
    text = body.get("text")
    if not text:
        return {"error": "Missing 'text' in request body"}, 422
    message = {"role": "user", "type": "message", "content": text}
    await from_user.put({"role": "user", "type": "message", "start": True})
    await from_user.put(message)
    await from_user.put({"role": "user", "type": "message", "end": True})


async def receive_messages(websocket: WebSocket):
    while True:
        try:
            try:
                data = await websocket.receive()
            except Exception as e:
                print(str(e))
                return

            if "text" in data:
                try:
                    data = json.loads(data["text"])
                    if data["role"] == "computer":
                        from_computer.put(
                            data
                        )  # To be handled by interpreter.computer.run
                    elif data["role"] == "user":
                        await from_user.put(data)
                    else:
                        raise ("Unknown role:", data)
                except json.JSONDecodeError:
                    pass  # data is not JSON, leave it as is
            elif "bytes" in data:
                data = data["bytes"]  # binary data
                await from_user.put(data)
        except WebSocketDisconnect as e:
            if e.code == 1000:
                logger.info("Websocket connection closed normally.")
                return
            else:
                raise


async def send_messages(websocket: WebSocket):
    while True:
        try:
            message = await to_device.get()
            # print(f"Sending to the device: {type(message)} {str(message)[:100]}")

            if isinstance(message, dict):
                await websocket.send_json(message)
            elif isinstance(message, bytes):
                await websocket.send_bytes(message)
            else:
                raise TypeError("Message must be a dict or bytes")
        except Exception as e:
            if message:
                # Make sure to put the message back in the queue if you failed to send it
                await to_device.put(message)
            raise

# TODO: These two methods should change to lifespan
@app.on_event("startup")
async def startup_event():
    print("")
    print_markdown("\n*Ready.*\n")
    print("")


@app.on_event("shutdown")
async def shutdown_event():
    print_markdown("*Server is shutting down*")
