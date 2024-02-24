from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
import json
from pathlib import Path
from interpreter import OpenInterpreter
from .system_messages.BaseSystemMessage import system_message


def configure_interpreter(interpreter: OpenInterpreter):
    
    ### SYSTEM MESSAGE
    interpreter.system_message = system_message

    ### LLM SETTINGS

    # Local settings
    # interpreter.llm.model = "local"
    # interpreter.llm.api_base = "https://localhost:8080/v1" # Llamafile default
    # interpreter.llm.max_tokens = 1000
    # interpreter.llm.context_window = 3000

    # Hosted settings
    interpreter.llm.api_key = os.getenv('OPENAI_API_KEY')
    interpreter.llm.model = "gpt-4"

    ### MISC SETTINGS

    interpreter.auto_run = True
    interpreter.computer.languages = [l for l in interpreter.computer.languages if l.name.lower() in ["applescript", "shell", "zsh", "bash", "python"]]
    interpreter.force_task_completion = False
    interpreter.offline = True
    interpreter.id = 206 # Used to identify itself to other interpreters. This should be changed programatically so it's unique.

    ### RESET conversations/user.json

    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_json_path = os.path.join(script_dir, 'conversations', 'user.json')
    with open(user_json_path, 'w') as file:
        json.dump([], file)

    ### SKILLS
    try:
        interpreter.computer.skills.path = Path(os.getenv('OI_SKILLS_PATH'))
        interpreter.computer.skills.import_skills()
    except:
        print("Temporarily skipping skills (OI 0.2.1, which is unreleased) so we can push to `pip`.")
        pass

    interpreter.computer.run("python", "tasks=[]")

    interpreter.computer.api_base = "https://oi-video-frame.vercel.app/"
    interpreter.computer.run("python","print('test')")

    return interpreter