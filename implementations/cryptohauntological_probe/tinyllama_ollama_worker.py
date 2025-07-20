import logging
from typing import List, Tuple


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')





from ollama import Client

class OllamaWorker:
    def __init__(self, host: str = "http://localhost:11434", model_name: str = "tinyllama"):
        self.client = Client(host=host)
        self.model_name = model_name

        

    # ------------------------------------------------------------------ #
    def _build_history(self,
                       history: List[Tuple[str, str]],
                       user_query: str) -> List[dict]:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({'role': 'user', 'content': user_turn})
            messages.append({'role': 'assistant', 'content': ai_turn})
        messages.append({'role': 'user', 'content': user_query})
        return messages

    # ------------------------------------------------------------------ #
    def reply(self,
              prompt: str,
              memory: List[Tuple[str, str]] | None = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)
        response = self.client.chat(model=self.model_name, messages=messages)
        return response['message']['content'].strip()

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    worker = OllamaWorker()
    memory = [("Hello", "Hi! How can I help you?")]
    text = worker.reply("The quick brown fox jumps over the lazy", memory)
    print(text)