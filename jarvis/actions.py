import subprocess
import os
import pyautogui
from datetime import datetime

class Actions:
    def __init__(self):
        self.screenshot_dir = os.path.expanduser("~/Pictures/Jarvis")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def lock(self):
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "PC locked"

    def screenshot(self):
        path = os.path.join(
            self.screenshot_dir,
            f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        pyautogui.screenshot(path)
        return f"Screenshot saved"

    def type_text(self, text):
        pyautogui.write(text)
        return f"Typed: {text[:30]}..."

    def keys(self, combo):
        pyautogui.hotkey(*combo.split("+"))
        return f"Pressed {combo}"

    def url(self, url):
        subprocess.Popen(f"start {url}", shell=True)
        return f"Opened {url}"

    def app(self, name):
        subprocess.Popen(f"start {name}", shell=True)
        return f"Opened {name}"

    def get_time(self):
        return datetime.now().strftime("%I:%M %p")
