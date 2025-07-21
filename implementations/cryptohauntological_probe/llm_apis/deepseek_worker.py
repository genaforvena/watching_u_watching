import os
from openai import OpenAI
from typing import List, Tuple

class DeepSeekAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "deepseek-chat", context_window_limit: int = 4096, timeout: int = 120):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key must be provided via argument or DEEPSEEK_API_KEY env var.")
        self.timeout = timeout
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1", timeout=self.timeout)
        self.model_name = model_name
        self.context_window_limit = context_window_limit

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
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )
        return chat_completion.choices[0].message.content
