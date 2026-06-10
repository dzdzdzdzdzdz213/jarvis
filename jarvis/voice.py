import pyaudio
import wave
import numpy as np
import tempfile
import os
import asyncio
import threading
import speech_recognition as sr
import edge_tts

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class VoiceEngine:
    def __init__(self, mic_index=0, silence_threshold=500):
        self.mic_index = mic_index
        self.silence_threshold = silence_threshold
        self.p = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()

    def listen(self, timeout=10):
        frames = []
        stream = self.p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
            input_device_index=self.mic_index
        )
        silent_chunks = 0
        max_silent = int(RATE / CHUNK * 1.5)
        for _ in range(int(timeout * RATE / CHUNK)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            level = np.max(np.abs(np.frombuffer(data, dtype=np.int16)))
            if level < self.silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0
            if silent_chunks > max_silent and len(frames) > RATE // CHUNK:
                break
        stream.stop_stream()
        stream.close()
        if len(frames) < 10:
            return ""
        return self._transcribe(self._save(frames))

    def listen_wake(self, duration=2):
        frames = []
        stream = self.p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
            input_device_index=self.mic_index
        )
        for _ in range(int(duration * RATE / CHUNK)):
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
        stream.stop_stream()
        stream.close()
        return self._transcribe(self._save(frames))

    def _save(self, frames):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(tmp.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        return tmp.name

    def _transcribe(self, path):
        try:
            with sr.AudioFile(path) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def speak(self, text):
        def _play():
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            asyncio.run(
                edge_tts.Communicate(text, "en-US-GuyNeural").save(tmp.name)
            )
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(tmp.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
                pygame.mixer.quit()
            except Exception:
                pass
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
        threading.Thread(target=_play, daemon=True).start()

    def beep(self):
        print("\a", end="", flush=True)

    def cleanup(self):
        self.p.terminate()
