"""
Responsible for taking an interpreter, then serving it at "/" as a POST SSE endpoint, accepting and streaming LMC Messages.

https://docs.openinterpreter.com/protocols/lmc-messages

Also needs to be saving conversations, and checking the queue.
"""

from typing import Generator
import uvicorn
from fastapi import FastAPI, Request, Response

def main(interpreter):

    app = FastAPI()

    @app.post("/")
    async def i_endpoint(request: Request) -> Response:
        async def event_stream() -> Generator[str, None, None]:
            data = await request.json()
            for response in interpreter.chat(message=data["message"], stream=True):
                yield response

        return Response(event_stream(), media_type="text/event-stream")
        
    uvicorn.run(app, host="0.0.0.0", port=8000)