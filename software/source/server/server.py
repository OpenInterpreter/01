from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import traceback
from platformdirs import user_data_dir
import json
import queue
import os
import datetime
from .utils.bytes_to_wav import bytes_to_wav
import re
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio
from .utils.kernel import put_kernel_messages_into_queue
from .i import configure_interpreter
from interpreter import interpreter
from ..utils.accumulator import Accumulator
from .utils.logs import setup_logging
from .utils.logs import logger

from ..utils.print_markdown import print_markdown

os.environ["STT_RUNNER"] = "server"
os.environ["TTS_RUNNER"] = "server"

markdown = """
○

*Starting...*
"""
print("")
print_markdown(markdown)
print("")


setup_logging()

accumulator = Accumulator()

app = FastAPI()

app_dir = user_data_dir("01")
conversation_history_path = os.path.join(app_dir, "conversations", "user.json")

SERVER_LOCAL_PORT = int(os.getenv("SERVER_LOCAL_PORT", 10001))


# This is so we only say() full sentences
def is_full_sentence(text):
    return text.endswith((".", "!", "?"))


def split_into_sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


# Queues
from_computer = (
    queue.Queue()
)  # Just for computer messages from the device. Sync queue because interpreter.run is synchronous
from_user = asyncio.Queue()  # Just for user messages from the device.
to_device = asyncio.Queue()  # For messages we send.

# Switch code executor to device if that's set

if os.getenv("CODE_RUNNER") == "device":
    # (This should probably just loop through all languages and apply these changes instead)

    class Python:
        # This is the name that will appear to the LLM.
        name = "python"

        def __init__(self):
            self.halt = False

        def run(self, code):
            """Generator that yields a dictionary in LMC Format."""

            # Prepare the data
            message = {
                "role": "assistant",
                "type": "code",
                "format": "python",
                "content": code,
            }

            # Unless it was just sent to the device, send it wrapped in flags
            if not (interpreter.messages and interpreter.messages[-1] == message):
                to_device.put(
                    {
                        "role": "assistant",
                        "type": "code",
                        "format": "python",
                        "start": True,
                    }
                )
                to_device.put(message)
                to_device.put(
                    {
                        "role": "assistant",
                        "type": "code",
                        "format": "python",
                        "end": True,
                    }
                )

            # Stream the response
            logger.info("Waiting for the device to respond...")
            while True:
                chunk = from_computer.get()
                logger.info(f"Server received from device: {chunk}")
                if "end" in chunk:
                    break
                yield chunk

        def stop(self):
            self.halt = True

        def terminate(self):
            """Terminates the entire process."""
            # dramatic!! do nothing
            pass

    interpreter.computer.languages = [Python]

# Configure interpreter
interpreter = configure_interpreter(interpreter)


@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    receive_task = asyncio.create_task(receive_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket))
    try:
        await asyncio.gather(receive_task, send_task)
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.info(f"Connection lost. Error: {e}")


@app.post("/")
async def add_computer_message(request: Request):
    body = await request.json()
    text = body.get("text")
    if not text:
        return {"error": "Missing 'text' in request body"}, 422
    message = {"role": "user", "type": "message", "content": text}
    await from_user.put({"role": "user", "type": "message", "start": True})
    await from_user.put(message)
    await from_user.put({"role": "user", "type": "message", "end": True})


async def receive_messages(websocket: WebSocket):
    while True:
        try:
            try:
                data = await websocket.receive()
            except Exception as e:
                print(str(e))
                return
            if "text" in data:
                try:
                    data = json.loads(data["text"])
                    if data["role"] == "computer":
                        from_computer.put(
                            data
                        )  # To be handled by interpreter.computer.run
                    elif data["role"] == "user":
                        await from_user.put(data)
                    else:
                        raise ("Unknown role:", data)
                except json.JSONDecodeError:
                    pass  # data is not JSON, leave it as is
            elif "bytes" in data:
                data = data["bytes"]  # binary data
                await from_user.put(data)
        except WebSocketDisconnect as e:
            if e.code == 1000:
                logger.info("Websocket connection closed normally.")
                return
            else:
                raise


async def send_messages(websocket: WebSocket):
    while True:
        message = await to_device.get()
        # print(f"Sending to the device: {type(message)} {str(message)[:100]}")

        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            elif isinstance(message, bytes):
                await websocket.send_bytes(message)
            else:
                raise TypeError("Message must be a dict or bytes")
        except:
            # Make sure to put the message back in the queue if you failed to send it
            await to_device.put(message)
            raise


async def listener():
    while True:
        try:
            while True:
                if not from_user.empty():
                    chunk = await from_user.get()
                    break
                elif not from_computer.empty():
                    chunk = from_computer.get()
                    break
                await asyncio.sleep(1)

            message = accumulator.accumulate(chunk)
            if message == None:
                # Will be None until we have a full message ready
                continue

            # print(str(message)[:1000])

            # At this point, we have our message

            if message["type"] == "audio" and message["format"].startswith("bytes"):
                if (
                    "content" not in message
                    or message["content"] == None
                    or message["content"] == ""
                ):  # If it was nothing / silence / empty
                    continue

                # Convert bytes to audio file
                # Format will be bytes.wav or bytes.opus
                mime_type = "audio/" + message["format"].split(".")[1]
                audio_file_path = bytes_to_wav(message["content"], mime_type)

                # For microphone debugging:
                if False:
                    os.system(f"open {audio_file_path}")
                    import time

                    time.sleep(15)

                text = stt(audio_file_path)
                print("> ", text)
                message = {"role": "user", "type": "message", "content": text}

            # At this point, we have only text messages

            if type(message["content"]) != str:
                print("This should be a string, but it's not:", message["content"])
                message["content"] = message["content"].decode()

            # Custom stop message will halt us
            if message["content"].lower().strip(".,! ") == "stop":
                continue

            # Load, append, and save conversation history
            with open(conversation_history_path, "r") as file:
                messages = json.load(file)
            messages.append(message)
            with open(conversation_history_path, "w") as file:
                json.dump(messages, file, indent=4)

            accumulated_text = ""

            if any(
                [m["type"] == "image" for m in messages]
            ) and interpreter.llm.model.startswith("gpt-"):
                interpreter.llm.model = "gpt-4-vision-preview"
                interpreter.llm.supports_vision = True

            for chunk in interpreter.chat(messages, stream=True, display=True):
                if any([m["type"] == "image" for m in interpreter.messages]):
                    interpreter.llm.model = "gpt-4-vision-preview"

                logger.debug("Got chunk:", chunk)

                # Send it to the user
                await to_device.put(chunk)
                # Yield to the event loop, so you actually send it out
                await asyncio.sleep(0.01)

                if os.getenv("TTS_RUNNER") == "server":
                    # Speak full sentences out loud
                    if (
                        chunk["role"] == "assistant"
                        and "content" in chunk
                        and chunk["type"] == "message"
                    ):
                        accumulated_text += chunk["content"]
                        sentences = split_into_sentences(accumulated_text)

                        # If we're going to speak, say we're going to stop sending text.
                        # This should be fixed probably, we should be able to do both in parallel, or only one.
                        if any(is_full_sentence(sentence) for sentence in sentences):
                            await to_device.put(
                                {"role": "assistant", "type": "message", "end": True}
                            )

                        if is_full_sentence(sentences[-1]):
                            for sentence in sentences:
                                await stream_tts_to_device(sentence)
                            accumulated_text = ""
                        else:
                            for sentence in sentences[:-1]:
                                await stream_tts_to_device(sentence)
                            accumulated_text = sentences[-1]

                        # If we're going to speak, say we're going to stop sending text.
                        # This should be fixed probably, we should be able to do both in parallel, or only one.
                        if any(is_full_sentence(sentence) for sentence in sentences):
                            await to_device.put(
                                {"role": "assistant", "type": "message", "start": True}
                            )

                # If we have a new message, save our progress and go back to the top
                if not from_user.empty():
                    # Check if it's just an end flag. We ignore those.
                    temp_message = await from_user.get()

                    if (
                        type(temp_message) is dict
                        and temp_message.get("role") == "user"
                        and temp_message.get("end")
                    ):
                        # Yup. False alarm.
                        continue
                    else:
                        # Whoops! Put that back
                        await from_user.put(temp_message)

                    with open(conversation_history_path, "w") as file:
                        json.dump(interpreter.messages, file, indent=4)

                    # TODO: is triggering seemingly randomly
                    # logger.info("New user message recieved. Breaking.")
                    # break

                # Also check if there's any new computer messages
                if not from_computer.empty():
                    with open(conversation_history_path, "w") as file:
                        json.dump(interpreter.messages, file, indent=4)

                    logger.info("New computer message recieved. Breaking.")
                    break
        except:
            traceback.print_exc()


async def stream_tts_to_device(sentence):
    force_task_completion_responses = [
        "the task is done",
        "the task is impossible",
        "let me know what you'd like to do next",
    ]
    if sentence.lower().strip().strip(".!?").strip() in force_task_completion_responses:
        return

    for chunk in stream_tts(sentence):
        await to_device.put(chunk)


def stream_tts(sentence):
    audio_file = tts(sentence)

    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    os.remove(audio_file)

    file_type = "bytes.raw"
    chunk_size = 1024

    # Stream the audio
    yield {"role": "assistant", "type": "audio", "format": file_type, "start": True}
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i : i + chunk_size]
        yield chunk
    yield {"role": "assistant", "type": "audio", "format": file_type, "end": True}


from uvicorn import Config, Server
import os
from importlib import import_module

# these will be overwritten
HOST = ""
PORT = 0


@app.on_event("startup")
async def startup_event():
    server_url = f"{HOST}:{PORT}"
    print("")
    print_markdown("\n*Ready.*\n")
    print("")


@app.on_event("shutdown")
async def shutdown_event():
    print_markdown("*Server is shutting down*")


async def main(
    server_host,
    server_port,
    llm_service,
    model,
    llm_supports_vision,
    llm_supports_functions,
    context_window,
    max_tokens,
    temperature,
    tts_service,
    stt_service,
):
    global HOST
    global PORT
    PORT = server_port
    HOST = server_host

    # Setup services
    application_directory = user_data_dir("01")
    services_directory = os.path.join(application_directory, "services")

    service_dict = {"llm": llm_service, "tts": tts_service, "stt": stt_service}

    # Create a temp file with the session number
    session_file_path = os.path.join(user_data_dir("01"), "01-session.txt")
    with open(session_file_path, "w") as session_file:
        session_id = int(datetime.datetime.now().timestamp() * 1000)
        session_file.write(str(session_id))

    for service in service_dict:
        service_directory = os.path.join(
            services_directory, service, service_dict[service]
        )

        # This is the folder they can mess around in
        config = {"service_directory": service_directory}

        if service == "llm":
            config.update(
                {
                    "interpreter": interpreter,
                    "model": model,
                    "llm_supports_vision": llm_supports_vision,
                    "llm_supports_functions": llm_supports_functions,
                    "context_window": context_window,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            )

        module = import_module(
            f".server.services.{service}.{service_dict[service]}.{service}",
            package="source",
        )

        ServiceClass = getattr(module, service.capitalize())
        service_instance = ServiceClass(config)
        globals()[service] = getattr(service_instance, service)

    interpreter.llm.completions = llm

    # Start listening
    asyncio.create_task(listener())

    # Start watching the kernel if it's your job to do that
    if True:  # in the future, code can run on device. for now, just server.
        asyncio.create_task(put_kernel_messages_into_queue(from_computer))

    config = Config(app, host=server_host, port=int(server_port), lifespan="on")
    server = Server(config)
    await server.serve()


# Run the FastAPI app
if __name__ == "__main__":
    asyncio.run(main())
