import sounddevice as sd
import wave
import numpy as np
import tempfile
import os
import subprocess
import textwrap
import time
import speech_recognition as sr

RATE = 16000
CHANNELS = 1

class VoiceEngine:
    def __init__(self, mic_index=-1, silence_threshold=0):
        self.mic_index = mic_index if mic_index >= 0 else 0
        self.recognizer = sr.Recognizer()
        if silence_threshold == 0:
            self._calibrate()
        else:
            self.silence_threshold = silence_threshold

    def _calibrate(self):
        frames = sd.rec(int(RATE), samplerate=RATE, channels=CHANNELS,
                        dtype='int16', device=self.mic_index)
        sd.wait()
        ambient = np.mean(np.abs(frames))
        self.silence_threshold = max(int(ambient * 2.5 + 200), 200)
        print(f"[Voice] Device {self.mic_index} ambient: {ambient:.0f}  threshold: {self.silence_threshold}")
        if ambient < 5:
            print("[Voice] Warning: mic may not be connected. Set MIC_INDEX in .env")

    def listen(self, timeout=10):
        frames = []
        silent_chunks = 0
        chunk_ms = 512
        max_silent = int(RATE / chunk_ms * 1.5)
        total = int(timeout * RATE / chunk_ms)

        try:
            with sd.InputStream(device=self.mic_index, samplerate=RATE, channels=CHANNELS,
                                dtype='int16', blocksize=chunk_ms) as stream:
                for _ in range(total):
                    data, _ = stream.read(chunk_ms)
                    frames.append(data)
                    level = np.max(np.abs(data))
                    if level < self.silence_threshold:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0
                    if silent_chunks > max_silent and len(frames) > RATE // chunk_ms:
                        break
        except Exception as e:
            print(f"[Mic Error] {e}")
            return ""

        if len(frames) < 10:
            return ""
        return self._transcribe(self._save(np.concatenate(frames)))

    def listen_wake(self, duration=2):
        try:
            frames = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS,
                            dtype='int16', device=self.mic_index)
            sd.wait()
            if np.max(np.abs(frames)) < 20:
                return ""
            return self._transcribe(self._save(frames))
        except Exception as e:
            return ""

    def _save(self, audio):
        audio = np.squeeze(audio)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(tmp.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(audio.astype(np.int16).tobytes())
        return tmp.name

    def _transcribe(self, path):
        try:
            with sr.AudioFile(path) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[STT] Google API error: {e}")
            return ""
        finally:
            for _ in range(3):
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                    break
                except PermissionError:
                    time.sleep(0.1)

    def speak(self, text):
        escaped = text.replace("'", "''").replace('"', '`"')
        ps = textwrap.dedent(f"""
        Add-Type -AssemblyName System.Speech
        $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $s.Speak('{escaped}')
        """)
        subprocess.run(['powershell', '-NoProfile', '-Command', ps], shell=True,
                      capture_output=True)

    def beep(self):
        import winsound
        winsound.Beep(800, 200)

    def cleanup(self):
        pass
