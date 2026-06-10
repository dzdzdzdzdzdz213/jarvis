## Setup

1. Install Python 3.10+
2. Clone and install:
```powershell
git clone https://github.com/dzdzdzdzdzdz213/jarvis
cd jarvis
pip install -r requirements.txt
```
3. Copy `.env.example` to `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_key_here
```

## Run

**Wake word mode** (say "Jarvis" then your command):
Set `MODE=wake` in `.env` and run:
```
python main.py
```

**Push-to-talk mode** (press Ctrl+Win+Space):
Set `MODE=ptt` in `.env` and run:
```
python main.py
```

## Commands

- "look" / "camera" / "what do you see" — takes a photo
- "lock my PC" — locks workstation
- "screenshot" — saves screenshot
- "what time is it" — tells the time
- "open youtube" / "open notepad" — opens apps/URLs
- "type hello world" — types text

## Config

Edit `.env`:
- `MODE`: `ptt` (push to talk) or `wake` (hands-free)
- `MIC_INDEX`: set if mic not detected (run `python -c "import sounddevice as sd; print(sd.query_devices())"`)
- `CAMERA_INDEX`: 0 for built-in webcam
- `SILENCE_THRESHOLD`: lower if not picking up, higher if too sensitive
