import os
import cohere
from typing import List, Tuple

class CohereAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "command-r-plus", context_window_limit: int = 2048, timeout: int = 120):
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key must be provided via argument or COHERE_API_KEY env var.")
        self.client = cohere.Client(api_key=self.api_key)
        self.model_name = model_name
        self.context_window_limit = context_window_limit
        self.timeout = timeout

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "USER", "message": user_turn})
            messages.append({"role": "CHATBOT", "message": ai_turn})
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        chat_history = self._build_history(memory, prompt)
        response = self.client.chat(
            model=self.model_name,
            message=prompt,
            chat_history=chat_history
        )
        return response.text
