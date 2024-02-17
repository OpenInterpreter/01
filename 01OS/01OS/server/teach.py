from datetime import datetime
from .utils.logs import setup_logging, logger
import tkinter as tk
import tkinter.simpledialog
from interpreter import interpreter
from tkinter import messagebox
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

def to_camel_case(text):
    words = text.split()
    camel_case_string = words[0].lower() + ''.join(word.title() for word in words[1:])
    return camel_case_string

def generate_python_code(function_name, steps, code):
    code_string = f'def {to_camel_case(function_name)}():\n'
    code_string += f'    """{function_name}"""\n'
    indented_code = textwrap.indent(code, '    ')
    code_string += indented_code + '\n'
    return code_string

def teach():
    root = tk.Tk()
    root.withdraw()

    skill_name = tkinter.simpledialog.askstring("Skill Name", "Please enter the name for the skill:")
    skill = Skill(skill_name)
    while True:
        step = tkinter.simpledialog.askstring("Next Step", "Enter the next step (or 'end' to finish): ")
        logger.info(f"Performing step: {step}")
        if step == "end":
            break

        chunk_code = ""
        for chunk in interpreter.chat(step, stream=True, display=False):
            if "format" in chunk and chunk["format"] == "execution":
                content = chunk["content"]
                language = content["format"]
                code = content["content"]
                chunk_code += code
                interpreter.computer.run(code, language)
            time.sleep(0.05)
            accumulator.accumulate(chunk)

        isCorrect = messagebox.askyesno("To Proceed?", "Did I do this step right?")
        if isCorrect:
            skill.steps.append(step)
            skill.code += chunk_code

    python_code = generate_python_code(skill.skill_name, skill.steps, skill.code)
    SKILLS_DIR = os.path.dirname(__file__) + "/skills"
    filename = os.path.join(SKILLS_DIR, f"{skill.skill_name.replace(' ', '_')}.py")
    with open(filename, "w") as file:
        file.write(python_code)
