import os
from dashscope import Generation
from typing import List, Tuple

class QwenAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "qwen-turbo", context_window_limit: int = 6144, timeout: int = 120):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("Qwen API key must be provided via argument or DASHSCOPE_API_KEY env var.")
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
        response = Generation.call(
            model=self.model_name,
            messages=messages,
            api_key=self.api_key,
            timeout=self.timeout
        )
        if response.status_code == 200:
            return response.output.text
        else:
            raise Exception(f"Qwen API error: {response.message}")
