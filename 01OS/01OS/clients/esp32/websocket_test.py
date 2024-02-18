#!/usr/bin/env python

"""A basic echo server for testing the device."""

import asyncio
import uuid
import websockets
from websockets.server import serve
import traceback


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


buffers: dict[uuid.UUID, bytearray] = {}


async def echo(websocket: websockets.WebSocketServerProtocol):
    async for message in websocket:
        try:
            if message == "s":
                print("starting stream for", websocket.id)
                buffers[websocket.id] = bytearray()
            elif message == "e":
                print("end, echoing stream for", websocket.id)
                await websocket.send("s")
                for chunk in divide_chunks(buffers[websocket.id], 1000):
                    await websocket.send(chunk)
                await websocket.send("e")
            elif type(message) is bytes:
                print("recvd", len(message), "bytes from", websocket.id)
                buffers[websocket.id].extend(message)
            else:
                print("ERR: recvd unknown message", message[:10], "from", websocket.id)
        except Exception as _e:
            traceback.print_exc()


async def main():
    async with serve(echo, "0.0.0.0", 9001):
        await asyncio.Future()  # run forever


asyncio.run(main())
