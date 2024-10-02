from __future__ import annotations
import sys
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
import os

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = openai.realtime.RealtimeModel(
        instructions="You are a helpful assistant and you love kittens",
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
        api_key=openai_api_key,
        base_url="wss://api.openai.com/v1",
    )
    assistant = MultimodalAgent(model=model)
    assistant.start(ctx.room)

    session = model.sessions[0]
    session.conversation.item.create(
      llm.ChatMessage(
        role="user",
        content="Please begin the interaction with the user in a manner consistent with your instructions.",
      )
    )
    session.response.create()

def main(livekit_url):
    # Workers have to be run as CLIs right now.
    # So we need to simualte running "[this file] dev"

    # Modify sys.argv to set the path to this file as the first argument
    # and 'dev' as the second argument
    sys.argv = [str(__file__), 'dev']

    # Initialize the worker with the entrypoint
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, api_key="devkey", api_secret="secret", ws_url=livekit_url, port=8082)
    )