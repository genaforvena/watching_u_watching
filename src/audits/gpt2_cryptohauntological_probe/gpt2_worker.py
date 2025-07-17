import logging
from typing import List, Tuple
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, pipeline
from langchain.memory import ConversationTokenBufferMemory
from langchain.chains import ConversationChain
import torch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.audits.gpt2_cryptohauntological_probe.base_generator import BaseGenerator

class GPT2Pipeline(HuggingFacePipeline):
    """HF pipeline that also exposes token counting."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.pipeline.tokenizer.name_or_path
        )
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

    def get_num_tokens(self, text: str) -> int:
        return len(self._tokenizer.encode(text))


class GPT2Worker:
    MAX_TOKENS = 1024
    MAX_HISTORY_TOKENS = 900

    def __init__(self, model_name: str = "gpt2-xl"):
        hf_pipe = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=model_name,
            max_new_tokens=self.MAX_TOKENS - self.MAX_HISTORY_TOKENS,
            temperature=0.7,
            top_k=40,
            repetition_penalty=1.2,
            pad_token_id=50256,
            device=0 if torch.cuda.is_available() else -1,
        )

        llm = GPT2Pipeline(pipeline=hf_pipe)

        # Now LangChain *knows* how many GPT-2 tokens each message costs.
        memory = ConversationTokenBufferMemory(
            llm=llm,
            max_token_limit=self.MAX_HISTORY_TOKENS,
            return_messages=True,
        )
        self.chat = ConversationChain(llm=llm, memory=memory)

    def reply(self, prompt: str, memory=None):
        memory = memory or []
        self.chat.memory.clear()
        for user, ai in memory:
            self.chat.memory.chat_memory.add_user_message(user)
            self.chat.memory.chat_memory.add_ai_message(ai)
        return self.chat.predict(input=prompt)

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    worker = GPT2Worker()
    memory = [("Hello", "Hi! How can I help you?")]
    text = worker.reply("The quick brown fox jumps over the lazy", memory)
    print(text)