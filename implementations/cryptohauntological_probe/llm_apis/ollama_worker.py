import ollama
from typing import List, Tuple

class OllamaAPIWorker:
    def __init__(self, model_name: str = "llama3", context_window_limit: int = 2048, timeout: int = 120):
        self.model_name = model_name
        self.context_window_limit = context_window_limit
        self.timeout = timeout

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "user", "content": user_turn})
            messages.append({"role": "assistant", "content": ai_turn})
        messages.append({"role": "user", "content": user_query})
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)
        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']