import argparse
import asyncio
import websockets
import os
import json

# Define the function to send audio file in chunks
async def send_audio_in_chunks(file_path, chunk_size=4096):
    async with websockets.connect("ws://localhost:8000/a") as websocket:
        # Send the start command with mime type
        await websocket.send(json.dumps({"action": "command", "state": "start", "mimeType": "audio/webm"}))

        # Open the file in binary mode and send in chunks
        with open(file_path, 'rb') as audio_file:
            chunk = audio_file.read(chunk_size)
            while chunk:
                await websocket.send(chunk)
                chunk = audio_file.read(chunk_size)

        # Send the end command
        await websocket.send(json.dumps({"action": "command", "state": "end"}))

        # Receive a json message and then close the connection
        message = await websocket.recv()
        print("Received message:", json.loads(message))
        await websocket.close()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Send a webm audio file to the /a websocket endpoint and print the responses.")
parser.add_argument("file_path", help="The path to the webm audio file to send.")
args = parser.parse_args()

# Check if the file exists
if not os.path.isfile(args.file_path):
    print(args.file_path)
    print("Error: The file does not exist.")
    exit(1)

# Run the asyncio event loop
asyncio.get_event_loop().run_until_complete(send_audio_in_chunks(args.file_path))
