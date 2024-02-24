from datetime import datetime
from .utils.logs import setup_logging, logger
from interpreter import interpreter as interpreter_core
from tkinter import messagebox, Button, simpledialog, Tk, Label, Frame, LEFT, ACTIVE
import time
import os
import textwrap
from .i import configure_interpreter
from .system_messages.TeachModeSystemMessage import system_message

setup_logging()
class Skill:
    def __init__(self, name: str):
        self.skill_name = name
        self.steps = []
        self.code = ""

class StepCheckDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Step Check")  # Set the title of the dialog window
        description = "Did I do this step correctly?"  # Add window description
        Label(master, text=description).pack()  # Display window description

    def buttonbox(self):
        box = Frame(self)
        Button(box, text="Yes", width=10, command=self.yes_action, default=ACTIVE).pack(side=LEFT, padx=5, pady=5)
        Button(box, text="No", width=10, command=self.no_action).pack(side=LEFT, padx=5, pady=5)
        Button(box, text="Task Complete", width=10, command=self.task_complete_action).pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.yes_action)
        self.bind("<Escape>", self.no_action)

        box.pack()

    def yes_action(self, event=None):
        self.result = "Yes"
        self.destroy()

    def no_action(self, event=None):
        self.result = "No"
        self.destroy()

    def task_complete_action(self, event=None):
        self.result = "Task Complete"
        self.destroy()

    def done(self, result):
        self.result = result
        self.destroy()

def to_camel_case(text):
    words = text.split()
    camel_case_string = words[0].lower() + ''.join(word.title() for word in words[1:])
    return camel_case_string

def generate_python_code(function_name, code):
    code_string = f'def {to_camel_case(function_name)}():\n'
    code_string += f'    """{function_name}"""\n'
    indented_code = textwrap.indent(code, '    ')
    code_string += indented_code + '\n'
    return code_string

def generate_python_steps(function_name, steps):
    code_string = f'def {to_camel_case(function_name)}():\n'
    code_string += f'    """{function_name}"""\n'
    code_string += f'    print({steps})\n'
    return code_string

def configure_interpreter_teach(interpreter):
    interpreter = configure_interpreter(interpreter)
    
    interpreter.computer.languages = [l for l in interpreter.computer.languages if l.name.lower() == "python"]
    interpreter.force_task_completion = True
    interpreter.os = True
    interpreter.llm.supports_vision = True
    interpreter.llm.model = "gpt-4-vision-preview"
    interpreter.llm.supports_functions = False
    interpreter.llm.context_window = 110000
    interpreter.llm.max_tokens = 4096
    interpreter.auto_run = True
    interpreter.system_message = system_message
    return interpreter

def teach():
    interpreter = configure_interpreter_teach(interpreter_core)
    root = Tk()
    root.withdraw()
    skill_name = simpledialog.askstring("Skill Name", "Please enter the name for the skill:", parent=root)
    isInit = False
    isWrong = False
    if skill_name:
        skill = Skill(skill_name)
        while True:
            if not isInit:
                step = simpledialog.askstring("First Step", "Enter the first step for the skill (or 'end' to finish): ", parent=root)
                isInit = True
            else:
                if isWrong:
                    step = simpledialog.askstring("Repeat Step", "Please re-phrase the step (or type 'end' to finish): ", parent=root)
                else:
                    step = simpledialog.askstring("Next Step", "Enter the next step (or 'end' to finish): ", parent=root)
            if step is None or step == "end":
                break
            elif step.strip() == "":
                continue
            logger.info(f"Performing step: {step}")
            root.update()
            chunk_code = ""
            for chunk in interpreter.chat(step, stream=True, display=True):
                if chunk["role"] == "computer" and "start" not in chunk and "end" not in chunk:
                    chunk_type = chunk["type"]
                    chunk_content = chunk["content"]
                    chunk_format = chunk["format"]
                    if chunk_type == "confirmation" and chunk_format == "execution" and chunk_content["type"] == "code" and chunk_content["format"] == "python":
                        chunk_code += chunk_content["content"]
                    elif chunk_type == "console" and chunk_format == "output" and ("Traceback" in chunk_content or "Error" in chunk_content or "Exception" in chunk_content):
                        # this was an error so we disregard chunk_code
                        chunk_code = ""
                time.sleep(0.05)
            
            stepCheckDialog = StepCheckDialog(root)
            stepCheckResult = stepCheckDialog.result
            if stepCheckResult == "Yes" or stepCheckResult == "Task Complete":
                isWrong = False
                skill.steps.append(step)
                skill.code += chunk_code
                if stepCheckResult == "Task Complete":
                    break
            elif stepCheckResult == "No":
                isWrong = True

        # Uncomment this incase you want steps instead of code
        #python_code = generate_python_steps(skill.skill_name, skill.steps)
        
        python_code = generate_python_code(skill.skill_name, skill.code)
        SKILLS_DIR = os.path.dirname(__file__) + "/skills"
        filename = os.path.join(SKILLS_DIR, f"{skill.skill_name.replace(' ', '_')}.py")
        logger.info(f"Saving skill to: {filename}")
        with open(filename, "w") as file:
            file.write(python_code)
