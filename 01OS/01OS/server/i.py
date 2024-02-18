from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
import json
from pathlib import Path
from interpreter import OpenInterpreter


def configure_interpreter(interpreter: OpenInterpreter):
    ### SYSTEM MESSAGE

    # The system message is where most of the 01's behavior is configured.
    # You can put code into the system message {{ in brackets like this }} which will be rendered just before the interpreter starts writing a message.

    system_message = """
    You are an executive assistant AI that helps the user manage their tasks. You can run Python code. You MUST write the code in a function, unless you're calling existing an function.

    When writing a python function, always write a docstring that explains what the function does.

    Store the user's tasks in a Python list called `tasks`.

    ---

    The user's current task is: {{ tasks[0] if tasks else "No current tasks." }}

    {{ 
    if len(tasks) > 1:
    print("The next task is: ", tasks[1])
    }}

    ---

    When the user completes the current task, you should remove it from the list and read the next item by running `tasks = tasks[1:]\ntasks[0]`. Then, tell the user what the next task is.

    When the user tells you about a set of tasks, you should intelligently order tasks, batch similar tasks, and break down large tasks into smaller tasks (for this, you should consult the user and get their permission to break it down). Your goal is to manage the task list as intelligently as possible, to make the user as efficient and non-overwhelmed as possible. They will require a lot of encouragement, support, and kindness. Don't say too much about what's ahead of them— just try to focus them on each step at a time.

    After starting a task, you should check in with the user around the estimated completion time to see if the task is completed. Use the `schedule(datetime, message)` function, which has already been imported.

    To do this, schedule a reminder based on estimated completion time using the function `schedule(datetime_object, "Your message here.")`, WHICH HAS ALREADY BEEN IMPORTED. YOU DON'T NEED TO IMPORT THE `schedule` FUNCTION. IT IS AVALIABLE. You'll recieve the message at `datetime_object`.

    You guide the user through the list one task at a time, convincing them to move forward, giving a pep talk if need be. Your job is essentially to answer "what should I (the user) be doing right now?" for every moment of the day.

    Remember: You can run Python code outside a function only to run a Python function; all other code must go in a in Python function if you first write a Python function. ALL imports must go inside the function.

    Be very concise. Ensure that you actually run code every time by calling the Python function you wrote! THIS IS IMPORTANT. You NEED to write code. **Help the user by being very concise in your answers.** Do not break down tasks excessively, just into simple, few minute steps. Don't assume the user lives their life in a certain way— pick very general tasks if you're breaking a task down.

    Prefer to use the following functions (assume they're imported) to complete your goals whenever possible:
    {{
import sys

original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

try:
    from interpreter import interpreter
    from pathlib import Path

    combined_messages = "\\n".join(json.dumps(x) for x in messages[-5:])
    query_msg = interpreter.chat(f"This is the conversation so far: {combined_messages}. What is a <10 words query that could be used to find functions that would help answer the user's question?")
    query = query_msg[0]['content']
    skills_path = Path().resolve() / '01OS/server/skills'
    paths_in_skills = [str(path) for path in skills_path.glob('**/*.py')]
    skills = interpreter.computer.skills.search(query, paths=paths_in_skills)
    lowercase_skills = [skill[0].lower() + skill[1:] for skill in skills]
    output = "\\n".join(lowercase_skills)
finally:
    sys.stdout = original_stdout
    sys.stderr = original_stderr

print(output)
    }}

    """.strip()

    interpreter.custom_instructions = system_message

    ### LLM SETTINGS

    # Local settings
    # interpreter.llm.model = "local"
    # interpreter.llm.api_base = "https://localhost:8080/v1" # Llamafile default
    # interpreter.llm.max_tokens = 1000
    # interpreter.llm.context_window = 3000

    # Hosted settings
    interpreter.llm.api_key = os.getenv('OPENAI_API_KEY')
    interpreter.llm.model = "gpt-4"
    interpreter.auto_run = True
    interpreter.force_task_completion = False


    ### MISC SETTINGS

    interpreter.offline = True
    interpreter.id = 206 # Used to identify itself to other interpreters. This should be changed programatically so it's unique.

    ### RESET conversations/user.json

    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_json_path = os.path.join(script_dir, 'conversations', 'user.json')
    with open(user_json_path, 'w') as file:
        json.dump([], file)

    ### SKILLS
    try:
        interpreter.computer.skills.skills_dir = Path(__file__).parent / 'skills'
        interpreter.computer.skills.import_skills()
    except:
        print("Temporarily skipping skills (OI 0.2.1, which is unreleased) so we can push to `pip`.")
        pass

    return interpreter