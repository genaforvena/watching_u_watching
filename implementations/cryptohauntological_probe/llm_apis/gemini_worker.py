import os
import google.generativeai as genai
from typing import List, Tuple

class GeminiAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-pro", context_window_limit: int = 2048, timeout: int = 120):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key must be provided via argument or GEMINI_API_KEY env var.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.context_window_limit = context_window_limit
        self.timeout = timeout

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "user", "parts": [user_turn]})
            messages.append({"role": "model", "parts": [ai_turn]})
        messages.append({"role": "user", "parts": [user_query]})
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        # The library manages history, so we just need to send the latest prompt
        response = self.model.generate_content(prompt)
        try:
            return response.text
        except ValueError:
            # If the response is blocked, return a message indicating that.
            return "[GEMINI_API_BLOCKED_RESPONSE]"
