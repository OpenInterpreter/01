from fastapi import FastAPI, WebSocket
import uvicorn
import json
from stt import stt
import tempfile

app = FastAPI()

@app.websocket("/user")
async def user(ws: WebSocket):
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
                        transcription = stt(audio_file, mime_type)
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