from interpreter import interpreter

# This is an Open Interpreter compatible profile.
# Visit https://01.openinterpreter.com/profile for all options.

# 01 suports OpenAI, ElevenLabs, and Coqui (Local) TTS providers
# {OpenAI: "openai", ElevenLabs: "elevenlabs", Coqui: "coqui"}
interpreter.tts = "elevenlabs"

# 01 Language Model Config.
interpreter.llm_service = "litellm"
interpreter.llm.model = "groq/llama3-8b-8192"
interpreter.llm.supports_vision = False
interpreter.llm.supports_functions = False
interpreter.llm.context_window = 2048
interpreter.llm.max_tokens = 4096
interpreter.llm.temperature = 0.8

# interpreter.llm.api_key = os.environ["GROQ_API_KEY"]

interpreter.computer.import_computer_api = False

interpreter.auto_run = True
interpreter.system_message = (
    "You are a helpful assistant that can answer questions and help with tasks."
)

# TODO: include other options in comments in the profiles for tts
# direct people to the profiles directory to make changes to the interpreter profile
# this should be made explicit on the docs

"""
    llm_service: str = "litellm",
    model: str = "gpt-4",
    llm_supports_vision: bool = False,
    llm_supports_functions: bool = False,
    context_window: int = 2048,
    max_tokens: int = 4096,
    temperature: float = 0.8,
    tts_service: str = "elevenlabs",
    stt_service: str = "openai",
"""
