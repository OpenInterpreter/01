"""
Exposes a SSE streaming server endpoint at /run, which recieves language and code,
and streams the output.
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import json
from interpreter import interpreter
import uvicorn

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

class Code(BaseModel):
    language: str
    code: str

app = FastAPI()

@app.post("/run")
async def run_code(code: Code):
    def generator():
        for chunk in interpreter.computer.run(code.language, code.code):
            yield json.dumps(chunk)
    return StreamingResponse(generator())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('COMPUTER_PORT', 9000)))
