import asyncio
import copy
import os
import re
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.transcription import STTSegmentsForwarder
from livekit.agents.llm import ChatContext, ChatMessage, LLMStream, ChatChunk, ChoiceDelta, Choice
from livekit import rtc
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero, elevenlabs
from dotenv import load_dotenv
import sys
import numpy as np
from typing import AsyncIterator
load_dotenv()

start_message = """Hi! You can hold the white circle below to speak to me.

Try asking what I can do."""

class ProcessedLLMStream(LLMStream):
    def __init__(
        self,
        original_stream: LLMStream,
        regex_pattern: str = r'<unvoiced code="([^"]+)"></unvoiced>',
    ) -> None:
        super().__init__(chat_ctx=original_stream.chat_ctx, fnc_ctx=original_stream.fnc_ctx)
        self.original_stream = original_stream
        self.regex_pattern = regex_pattern
        self.init_match = '<.*?'                    # match for the '<' and any characters to the left of it
        self.accumulating = False
        self._aiter = self._process_stream()
        self._buffer = ""


    async def _process_stream(self) -> AsyncIterator[ChatChunk]:
        async for chunk in self.original_stream:
            new_choices = []
            for choice in chunk.choices:
                content = choice.delta.content

                if content:
                    init_match = re.search(self.init_match, content)
                    if init_match:
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        print("INITIAL MATCH FOUND!!!!!!")
                        self.accumulating = True
                    if self.accumulating:
                        self._buffer += content
                        print("ACCUMULATING BUFFER!!!")
                        print("ACCUMULATING BUFFER!!!")
                        print("ACCUMULATING BUFFER!!!")
                        print("ACCUMULATING BUFFER!!!")
                        print("ACCUMULATING BUFFER!!!")
                        print("ACCUMULATING BUFFER!!!")
                        match = re.search(self.regex_pattern, self._buffer)
                        if match:
                            code = match.group(1)
                            print(f"Extracted Code: {code}")  

                            # Create a confirmation message
                            confirmation_msg = ChatMessage(
                                role="assistant",
                                content=f"Code extracted: {code}",
                            )

                            # Wrap the confirmation message in ChoiceDelta and Choice
                            choice_delta = ChoiceDelta(
                                role=confirmation_msg.role,
                                content=str(confirmation_msg.content)   # we know confirmation_msg.content is a string
                            )
                            new_choice = Choice(
                                delta=choice_delta,
                                index=choice.index
                            )

                            # Create a new ChatChunk with the confirmation Choice
                            confirmation_chunk = ChatChunk(choices=[new_choice])

                            # Yield the confirmation chunk
                            yield confirmation_chunk
                            self.accumulating = False
                            self._buffer = ""
                        continue  # Skip yielding the original content
                new_choices.append(choice)
            if new_choices:
                yield ChatChunk(choices=new_choices)

    async def __anext__(self) -> ChatChunk:
        try:
            return await self._aiter.__anext__()
        except StopAsyncIteration:
            await self.aclose()
            raise

def _01_synthesize_assistant_reply(
    assistant: VoiceAssistant, chat_ctx: ChatContext
) -> LLMStream:
    """
    Custom function to process the OpenAI compatible endpoint's output.
    Extracts code from responses matching the <unvoiced code=...></unvoiced> pattern.

    Args:
        assistant (VoiceAssistant): The VoiceAssistant instance.
        chat_ctx (ChatContext): The current chat context.

    Returns:
        LLMStream: The processed LLMStream.
    """
    llm_stream = assistant.llm.chat(chat_ctx=chat_ctx, fnc_ctx=assistant.fnc_ctx)
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")
    print("HELLO FROM INSIDE OUR CUSTOM LLM STREAM")

    return ProcessedLLMStream(original_stream=llm_stream)

# This function is the entrypoint for the agent.
async def entrypoint(ctx: JobContext):
    # Create an initial chat context with a system prompt
    initial_ctx = ChatContext().append(
        role="system",
        text=(
            "" # Open Interpreter handles this.
        ),
    )

    # Connect to the LiveKit room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create a black background with a white circle
    width, height = 640, 480
    image_np = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Create a white circle
    center = (width // 2, height // 2)
    radius = 50
    y, x = np.ogrid[:height, :width]
    mask = ((x - center[0])**2 + (y - center[1])**2) <= radius**2
    image_np[mask] = [255, 255, 255, 255]  # White color with full opacity

    source = rtc.VideoSource(width, height)
    track = rtc.LocalVideoTrack.create_video_track("static_image", source)
    
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    publication = await ctx.room.local_participant.publish_track(track, options)

    # Function to continuously publish the static image
    async def publish_static_image():
        while True:
            frame = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGBA, image_np.tobytes())
            source.capture_frame(frame)
            await asyncio.sleep(1/30)  # Publish at 30 fps

    # Start publishing the static image
    asyncio.create_task(publish_static_image())

    # VoiceAssistant is a class that creates a full conversational AI agent.
    # See https://github.com/livekit/agents/blob/main/livekit-agents/livekit/agents/voice_assistant/assistant.py
    # for details on how it works.

    interpreter_server_host = os.getenv('INTERPRETER_SERVER_HOST', 'localhost')
    interpreter_server_port = os.getenv('INTERPRETER_SERVER_PORT', '8000')
    base_url = f"http://{interpreter_server_host}:{interpreter_server_port}/openai"

    # For debugging
    # base_url = "http://127.0.0.1:8000/openai"

    open_interpreter = openai.LLM(
        model="open-interpreter", base_url=base_url, api_key="x"
    )

    tts_provider = os.getenv('01_TTS', '').lower()
    stt_provider = os.getenv('01_STT', '').lower()

    # Add plugins here
    if tts_provider == 'openai':
        tts = openai.TTS()
    elif tts_provider == 'elevenlabs':
        tts = elevenlabs.TTS()
    elif tts_provider == 'cartesia':
        pass # import plugin, TODO support this
    else:
        raise ValueError(f"Unsupported TTS provider: {tts_provider}. Please set 01_TTS environment variable to 'openai' or 'elevenlabs'.")

    if stt_provider == 'deepgram':
        stt = deepgram.STT()
    else:
        raise ValueError(f"Unsupported STT provider: {stt_provider}. Please set 01_STT environment variable to 'deepgram'.")

    assistant = VoiceAssistant(
        vad=silero.VAD.load(),  # Voice Activity Detection
        stt=stt,  # Speech-to-Text
        llm=open_interpreter,  # Language Model
        tts=tts,  # Text-to-Speech
        chat_ctx=initial_ctx,  # Chat history context
        # will_synthesize_assistant_reply=_01_synthesize_assistant_reply,
    )

    chat = rtc.ChatManager(ctx.room)

    async def _answer_from_text(text: str):
        chat_ctx = copy.deepcopy(assistant._chat_ctx)
        chat_ctx.messages.append(ChatMessage(role="user", content=text))

        stream = open_interpreter.chat(chat_ctx=chat_ctx)
        await assistant.say(stream)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if not msg.message:
            return
        asyncio.create_task(_answer_from_text(msg.message))

    # Start the voice assistant with the LiveKit room
    assistant.start(ctx.room)

    await asyncio.sleep(1)

    print("HELLO FROM INSIDE THE WORKER")
    print("HELLO FROM INSIDE THE WORKER")
    print("HELLO FROM INSIDE THE WORKER")
    print("HELLO FROM INSIDE THE WORKER")
    print("HELLO FROM INSIDE THE WORKER")

    # Greets the user with an initial message
    await assistant.say(start_message,
    allow_interruptions=True)

    stt_forwarder = STTSegmentsForwarder(room=ctx.room, participant=ctx.room.local_participant)
    await stt_forwarder._run()


def main(livekit_url):
    print("Starting worker!!!!!!! 🦅🦅🦅🦅🦅🦅")
    print("Starting worker!!!!!!! 🦅🦅🦅🦅🦅🦅")
    print("Starting worker!!!!!!! 🦅🦅🦅🦅🦅🦅")
    print("Starting worker!!!!!!! 🦅🦅🦅🦅🦅🦅")
    print("Starting worker!!!!!!! 🦅🦅🦅🦅🦅🦅")
    # Workers have to be run as CLIs right now.
    # So we need to simualte running "[this file] dev"

    # Modify sys.argv to set the path to this file as the first argument
    # and 'dev' as the second argument
    sys.argv = [str(__file__), 'dev']

    # Initialize the worker with the entrypoint
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, api_key="devkey", api_secret="secret", ws_url=livekit_url, port=8082)
    )