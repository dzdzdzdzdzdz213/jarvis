import requests

SYSTEM_PROMPT = """You are Jarvis, a desktop AI assistant for Windows 11. Be concise and natural.

AVAILABLE ACTIONS (you decide when to use them based on the user's request):
- camera: take a photo (user says "look", "camera", "photo", "who is there", "what do you see")
- lock: lock the PC
- screenshot: take a screenshot of the screen
- type: type text on the keyboard
- keys: press a keyboard shortcut (e.g., "ctrl+c")
- url: open a URL in the browser
- app: open an application
- time: tell the current time
- timer: set a timer for N minutes

Respond with what you did. Keep responses under 2 sentences unless asked for more."""

class LLM:
    def __init__(self, api_key, model="meta-llama/llama-3.3-70b-instruct"):
        self.api_key = api_key
        self.model = model
        self.history = []

    def ask(self, prompt, system=SYSTEM_PROMPT):
        messages = [{"role": "system", "content": system}]
        for h in self.history[-6:]:
            messages.append(h)
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/jarvis",
                    "X-Title": "Jarvis"
                },
                json={"model": self.model, "messages": messages},
                timeout=30
            )
            data = resp.json()
            if "error" in data:
                return f"API error: {data['error'].get('message', str(data['error']))}"
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except requests.exceptions.Timeout:
            return "Request timed out. Try again."
        except Exception as e:
            return f"Error: {e}"
