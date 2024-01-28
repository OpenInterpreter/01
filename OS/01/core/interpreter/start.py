"""
Responsible for configuring an interpreter, then using main.py to serve it at "/".
"""

from main import main
from interpreter import interpreter
import os
import glob

### SYSTEM MESSAGE

# The system message is where most of the 01's behavior is configured.
# You can put code into the system message {{ in brackets like this }} which will be rendered just before the interpreter starts writing a message.

system_message = """

You are an executive assistant AI that helps the user manage their tasks. You can run Python code.

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

To do this, schedule a reminder based on estimated completion time using `computer.clock.schedule(datetime_object, "Your message here.")`. You'll recieve the message at `datetime_object`.

You guide the user through the list one task at a time, convincing them to move forward, giving a pep talk if need be. Your job is essentially to answer "what should I (the user) be doing right now?" for every moment of the day.

""".strip()

interpreter.system_message = system_message


### TOOLS

for file in glob.glob('/tools/*.py'):
    with open(file, 'r') as f:
        interpreter.computer.run("python", f.read())


### LLM SETTINGS

# Local settings
# interpreter.llm.model = "local"
# interpreter.llm.api_base = "https://localhost:8080/v1" # Llamafile default
# interpreter.llm.max_tokens = 1000
# interpreter.llm.context_window = 3000

# Hosted settings
interpreter.llm.api_key = os.getenv('OPENAI_API_KEY')
interpreter.llm.model = "gpt-3.5-turbo"


### MISC SETTINGS

interpreter.offline = True
interpreter.id = 206 # Used to identify itself to other interpreters. This should be changed programatically so it's unique.


### SERVE INTERPRETER AT "/"

main(interpreter)