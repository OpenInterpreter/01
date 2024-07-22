"""
Mac only.
"""

import subprocess
import threading
import time

def beep(sound):
    if "." not in sound:
        sound = sound + ".aiff"
    try:
        subprocess.Popen(["afplay", f"/System/Library/Sounds/{sound}"])
    except:
        pass  # No big deal

class RepeatedBeep:
    def __init__(self):
        self.sound = "Pop"
        self.running = False
        self.thread = threading.Thread(target=self._play_sound, daemon=True)
        self.thread.start()

    def _play_sound(self):
        while True:
            if self.running:
                try:
                    subprocess.call(["afplay", f"/System/Library/Sounds/{self.sound}.aiff"])
                except:
                    pass  # No big deal
                time.sleep(0.6)
            time.sleep(0.05)

    def start(self):
        if not self.running:
            time.sleep(0.6*4)
            self.running = True   

    def stop(self):
        self.running = False

beeper = RepeatedBeep()