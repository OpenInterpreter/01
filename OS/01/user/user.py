"""
Handles everything the user interacts through.

Connects to a websocket at /user. Sends shit to it, and displays/plays the shit it sends back.

For now, just handles a spacebar being pressed— for the duration it's pressed,
it should record audio.

SIMPLEST POSSIBLE: Sends that audio to OpenAI whisper, gets the transcript,
sends it to /user in LMC format (role: user, etc)

MOST FUTUREPROOF: Streams chunks of audio to /user, which will then handle stt in stt.py.
"""