"""
Responsible for taking an interpreter, then serving it at "/" as a websocket, accepting and streaming LMC Messages.

https://docs.openinterpreter.com/protocols/lmc-messages

Also needs to be saving conversations, and checking the queue.
"""

import uvicorn
from fastapi import FastAPI, WebSocket
import asyncio
import json

def main(interpreter):

    app = FastAPI()

    @app.websocket("/")
    async def i_test(websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            while data.strip().lower() != "stop":  # Stop command
                task = asyncio.create_task(websocket.receive_text())

                # This would be terrible for production. Just for testing.
                try:
                    data_dict = json.loads(data)
                    if set(data_dict.keys()) == {"role", "content", "type"} or set(
                        data_dict.keys()
                    ) == {"role", "content", "type", "format"}:
                        data = data_dict
                except json.JSONDecodeError:
                    pass

                for response in interpreter.chat(
                    message=data, stream=True, display=False
                ):
                    if task.done():
                        data = task.result()  # Get the new message
                        break  # Break the loop and start processing the new message
                    # Send out assistant message chunks
                    if (
                        response.get("type") == "message"
                        and response["role"] == "assistant"
                        and "content" in response
                    ):
                        await websocket.send_text(response["content"])
                        await asyncio.sleep(0.01)  # Add a small delay
                    if (
                        response.get("type") == "message"
                        and response["role"] == "assistant"
                        and response.get("end") == True
                    ):
                        await websocket.send_text("\n")
                        await asyncio.sleep(0.01)  # Add a small delay
                if not task.done():
                    data = (
                        await task
                    )  # Wait for the next message if it hasn't arrived yet
        
    uvicorn.run(app, host="0.0.0.0", port=8000)