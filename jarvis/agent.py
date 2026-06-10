import time
import os
import threading
from pynput import keyboard as pynput_kb
from jarvis.voice import VoiceEngine
from jarvis.vision import Camera
from jarvis.llm import LLM
from jarvis.actions import Actions
from jarvis import config

class Agent:
    def __init__(self):
        self.voice = VoiceEngine(config.MIC_INDEX, config.SILENCE_THRESHOLD)
        self.camera = Camera(config.CAMERA_INDEX)
        self.llm = LLM(config.OPENROUTER_API_KEY, config.OPENROUTER_MODEL)
        self.actions = Actions()
        self.running = True

    def _run_actions(self, text):
        t = text.lower()
        results = []
        if "camera" in t or "photo" in t or "look" in t or "who" in t or "see" in t:
            if path := self.camera.capture():
                results.append(f"[Camera] Photo taken: {path}")
        if "lock" in t or "lockdown" in t:
            results.append(f"[Action] {self.actions.lock()}")
        if "screenshot" in t or "capture screen" in t:
            results.append(f"[Action] {self.actions.screenshot()}")
        if "time" in t or "what time" in t:
            results.append(f"[Action] It's {self.actions.get_time()}")
        for r in results:
            print(r)
        return results

    def process(self, text):
        if not text:
            return None
        print(f"[You] {text}")
        action_results = self._run_actions(text)
        response = self.llm.ask(text)
        if response and not response.startswith("Error") and not response.startswith("API error"):
            print(f"[Jarvis] {response}")
            self.voice.speak(response)
        elif response:
            print(f"[Jarvis] {response}")
        return response

    def start_push_to_talk(self):
        print("[Jarvis] Ready. Press Ctrl+Win+Space to talk. Ctrl+C to quit.")

        def on_activate():
            print("\n[System] Listening... (speak now)")
            text = self.voice.listen(timeout=10)
            self.process(text)

        hotkey = pynput_kb.HotKey(
            pynput_kb.HotKey.parse("<ctrl>+<win>+<space>"),
            on_activate
        )

        def for_canonical(f):
            return lambda k: f(hotkey.canonical(k))

        with pynput_kb.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass
            finally:
                self.running = False

    def start_wake_word(self):
        print(f"[Jarvis] Listening for '{config.WAKE_WORD}'... Ctrl+C to quit.")
        while self.running:
            try:
                text = self.voice.listen_wake(duration=2)
                if text and config.WAKE_WORD in text:
                    self.voice.beep()
                    print(f"\n[System] Wake word detected. Listening for command...")
                    cmd = self.voice.listen(timeout=8)
                    self.process(cmd)
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

    def run(self):
        try:
            if config.MODE == "wake":
                self.start_wake_word()
            else:
                self.start_push_to_talk()
        except KeyboardInterrupt:
            pass
        finally:
            self.voice.cleanup()
            print("[Jarvis] Shutdown complete.")
