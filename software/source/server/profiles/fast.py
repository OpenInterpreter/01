async def main(server_host, server_port, tts_service, asynchronous):

    if asynchronous:

        base_interpreter.system_message = (
            "You are a helpful assistant that can answer questions and help with tasks."
        )

        base_interpreter.computer.import_computer_api = False

        base_interpreter.llm.model = "groq/llama3-8b-8192"

        base_interpreter.llm.api_key = os.environ["GROQ_API_KEY"]

        base_interpreter.llm.supports_functions = False

        base_interpreter.auto_run = True

        base_interpreter.tts = tts_service

        interpreter = AsyncInterpreter(base_interpreter)

    else:

        configured_interpreter = configure_interpreter(base_interpreter)

        configured_interpreter.llm.supports_functions = True

        configured_interpreter.tts = tts_service

        interpreter = AsyncInterpreter(configured_interpreter)
