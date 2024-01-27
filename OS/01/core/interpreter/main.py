"""
Responsible for taking an interpreter, then serving it at "/" as a POST SSE endpoint, accepting and streaming LMC Messages.

https://docs.openinterpreter.com/protocols/lmc-messages

Also needs to be saving conversations, and checking the queue.
"""

from typing import Generator
import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.exceptions import DisconnectedClientError

def main(interpreter):

    app = FastAPI()

    @app.post("/")
    async def i_endpoint(request: Request) -> Response:
        async def event_stream() -> Generator[str, None, None]:
            data = await request.json()
            # TODO: Save conversation to /conversations
            try:
                for response in interpreter.chat(message=data["message"], stream=True):
                    yield response
                    # TODO: Check queue. Do we need to break (I guess we need a while loop around this..?)
                    # and handle the new message from the queue? Then delete the message from the queue.
            except DisconnectedClientError:
                print("Client disconnected")
                # TODO: Save conversation to /conversations
        return Response(event_stream(), media_type="text/event-stream")
        
    uvicorn.run(app, host="0.0.0.0", port=8000)