from .check_filtered_kernel import check_filtered_kernel
import asyncio

async def put_kernel_messages_into_queue(queue):
    while True:
        text = check_filtered_kernel()
        if text:
            if isinstance(queue, asyncio.Queue):
                await queue.put({"role": "computer", "type": "console", "start": True})
                await queue.put({"role": "computer", "type": "console", "format": "output", "content": text})
                await queue.put({"role": "computer", "type": "console", "end": True})
            else:
                queue.put({"role": "computer", "type": "console", "start": True})
                queue.put({"role": "computer", "type": "console", "format": "output", "content": text})
                queue.put({"role": "computer", "type": "console", "end": True})
        
        await asyncio.sleep(5)