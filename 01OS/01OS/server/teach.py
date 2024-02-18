from datetime import datetime
from .utils.logs import setup_logging, logger
from interpreter import interpreter
from tkinter import messagebox, Button, simpledialog, Tk, Label, Frame, LEFT, ACTIVE
from ..utils.accumulator import Accumulator
import time
import os
import textwrap

setup_logging()
accumulator = Accumulator()
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

def teach():
    root = Tk()
    root.withdraw()

    skill_name = simpledialog.askstring("Skill Name", "Please enter the name for the skill:")
    skill = Skill(skill_name)
    while True:
        step = simpledialog.askstring("Next Step", "Enter the next step (or 'end' to finish): ")
        logger.info(f"Performing step: {step}")
        if step == "end":
            break

        chunk_code = ""
        interpreter.computer.languages = [l for l in interpreter.computer.languages if l.name.lower() == "python"]
        interpreter.force_task_completion = True
        for chunk in interpreter.chat(step, stream=True, display=False):
            if "format" in chunk and chunk["format"] == "execution":
                content = chunk["content"]
                language = content["format"]
                code = content["content"]
                chunk_code += code
                interpreter.computer.run(code, language)
            time.sleep(0.05)
            accumulator.accumulate(chunk)

        stepCheckDialog = StepCheckDialog(root)
        stepCheckResult = stepCheckDialog.result

        if stepCheckResult == "Yes" or stepCheckResult == "Task Complete":
            skill.steps.append(step)
            skill.code += chunk_code
            if stepCheckResult == "Task Complete":
                break

    # Uncomment this incase you want steps instead of code
    #python_code = generate_python_steps(skill.skill_name, skill.steps)
    
    python_code = generate_python_code(skill.skill_name, skill.code)
    SKILLS_DIR = os.path.dirname(__file__) + "/skills"
    filename = os.path.join(SKILLS_DIR, f"{skill.skill_name.replace(' ', '_')}.py")
    with open(filename, "w") as file:
        file.write(python_code)
