from fastapi import FastAPI, Request, WebSocket
import uvicorn
import redis
import json
from dotenv import load_dotenv
from stt import get_transcription
import tempfile

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/i/")
async def i(request: Request):
    message = await request.json()

    client_host = request.client.host  # Get the client's IP address

    message = f"""

    Another interpreter sent this message to you: {message}
    To respond, send a POST request to {client_host}/i/.

    """.strip()

    r.lpush("to_main", {
        "role": "computer",
        "type": "message",
        "content": message
    })


@app.websocket("/a")
async def a(ws: WebSocket):
    await ws.accept()
    audio_file = bytearray()
    mime_type = None

    try:
        while True:
            message = await ws.receive()

            if message['type'] == 'websocket.disconnect':
                break

            if message['type'] == 'websocket.receive':
                if 'text' in message:
                    control_message = json.loads(message['text'])
                    if control_message.get('action') == 'command' and control_message.get('state') == 'start' and 'mimeType' in control_message:
                        # This indicates the start of a new audio file
                        mime_type = control_message.get('mimeType')
                    elif control_message.get('action') == 'command' and control_message.get('state') == 'end':
                        # This indicates the end of the audio file
                        # Process the complete audio file here
                        transcription = get_transcription(audio_file, mime_type)
                        await ws.send_json({"transcript": transcription})
                        
                        print("SENT TRANSCRIPTION!")

                        # Reset the bytearray for the next audio file
                        audio_file = bytearray()
                        mime_type = None
                elif 'bytes' in message:
                    # If it's not a control message, it's part of the audio file
                    audio_file.extend(message['bytes'])
                    
    except Exception as e:
        print(f"WebSocket connection closed with exception: {e}")
    finally:
        await ws.close()
        print("WebSocket connection closed")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory():
        uvicorn.run(app, host="0.0.0.0", port=8000)
