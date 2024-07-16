from interpreter import AsyncInterpreter
interpreter = AsyncInterpreter()

# This is an Open Interpreter compatible profile.
# Visit https://01.openinterpreter.com/profile for all options.

# 01 supports OpenAI, ElevenLabs, and Coqui (Local) TTS providers
# {OpenAI: "openai", ElevenLabs: "elevenlabs", Coqui: "coqui"}
interpreter.tts = "elevenlabs"

interpreter.llm.model = "groq/llama3-70b-8192"
interpreter.llm.supports_vision = False
interpreter.llm.supports_functions = False
interpreter.llm.context_window = 8000
interpreter.llm.max_tokens = 1000
interpreter.llm.temperature = 0

interpreter.computer.import_computer_api = False

interpreter.auto_run = True
interpreter.system_message = (
    "You are a helpful assistant that can answer questions and help with tasks."
)
