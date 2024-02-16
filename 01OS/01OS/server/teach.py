from datetime import datetime

class Skill:
    def __init__(self, name: str):
        self.skill_name = name
        self.steps = []
    
    def teach(self, code: str):
        self.steps.append(code)