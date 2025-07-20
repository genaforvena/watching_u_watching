import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import List, Tuple

class MistralAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "mistral-large-latest"):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key must be provided via argument or MISTRAL_API_KEY env var.")
        self.client = MistralClient(api_key=self.api_key)
        self.model_name = model_name

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append(ChatMessage(role="user", content=user_turn))
            messages.append(ChatMessage(role="assistant", content=ai_turn))
        messages.append(ChatMessage(role="user", content=user_query))
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)
        chat_response = self.client.chat(
            model=self.model_name,
            messages=messages,
        )
        return chat_response.choices[0].message.content
