import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
MIC_INDEX = int(os.getenv("MIC_INDEX", "0"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower()
SILENCE_THRESHOLD = int(os.getenv("SILENCE_THRESHOLD", "500"))
MODE = os.getenv("MODE", "ptt")
