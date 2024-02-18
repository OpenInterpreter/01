#!/usr/bin/env python

import asyncio
import simpleaudio as sa
from websockets.server import serve


def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 


async def echo(websocket):
    async for message in websocket:
        try:
            play_obj = sa.play_buffer(bytearray(message), 1, 2, 16000)
            play_obj.wait_done()

            x = list(divide_chunks(bytearray(message), 1000)) 
            for i in x:
                await websocket.send(i)

        except Exception as e:
            print('fail')



async def main():
    async with serve(echo, "0.0.0.0", 9001):
        await asyncio.Future()  # run forever

asyncio.run(main())