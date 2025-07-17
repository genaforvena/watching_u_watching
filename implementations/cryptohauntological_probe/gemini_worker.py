import os
import requests
from typing import List, Tuple

class GeminiAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key must be provided via argument or GEMINI_API_KEY env var.")
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:generateContent?key={self.api_key}"

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "user", "parts": [{"text": user_turn}]})
            messages.append({"role": "model", "parts": [{"text": ai_turn}]})
        messages.append({"role": "user", "parts": [{"text": user_query}]})
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)
        data = {"contents": messages}
        response = requests.post(self.api_url, json=data)
        response.raise_for_status()
        candidates = response.json().get("candidates", [])
        if not candidates:
            return "[GEMINI_API_NO_RESPONSE]"
        return candidates[0]["content"]["parts"][0]["text"].strip()
