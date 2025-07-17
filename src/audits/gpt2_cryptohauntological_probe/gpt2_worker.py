import logging
from typing import List, Tuple
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, pipeline
from langchain.memory import ConversationTokenBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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


MODEL_NAME = "gpt2-xl"
MAX_CONTEXT = 1024           # hard GPT-2 limit
MAX_NEW     = 100            # how many tokens we allow the model to add
MAX_INPUT   = MAX_CONTEXT - MAX_NEW


class GPT2Worker:
    def __init__(self, model_name: str = MODEL_NAME):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        hf_pipe = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=self.tokenizer,
            max_new_tokens=50,
            temperature=0.7,
            top_k=40,
            repetition_penalty=1.2,
            pad_token_id=self.tokenizer.eos_token_id,
            device=0 if torch.cuda.is_available() else -1,
        )

        self.llm = HuggingFacePipeline(pipeline=hf_pipe)

        # A very small prompt template that simply concatenates
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="{history}\nUser: {input}\nAssistant:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    # ------------------------------------------------------------------ #
    def _build_history(self,
                       history: List[Tuple[str, str]],
                       user_query: str) -> str:
        """
        Return a string containing the conversation history truncated so that
        the *whole* prompt fits into MAX_INPUT tokens.
        Keeps the most recent turns.
        """
        # Build list of strings in chronological order
        turns = []
        for user_turn, ai_turn in history:
            turns.append(f"User: {user_turn}\nAssistant: {ai_turn}")

        # Add the current query
        turns.append(f"User: {user_query}\nAssistant:")

        # Encode the full thing once
        full_text = "\n".join(turns)
        token_ids = self.tokenizer.encode(full_text)

        if len(token_ids) <= MAX_INPUT:
            return "\n".join(turns[:-1])  # remove the trailing "Assistant:"

        # Truncate from the front until it fits
        # (keep at least the last turn)
        while len(token_ids) > MAX_INPUT and len(turns) > 1:
            turns.pop(0)
            full_text = "\n".join(turns)
            token_ids = self.tokenizer.encode(full_text)

        return "\n".join(turns[:-1])

    # ------------------------------------------------------------------ #
    def reply(self,
              prompt: str,
              memory: List[Tuple[str, str]] | None = None) -> str:
        memory = memory or []
        history_str = self._build_history(memory, prompt)
        answer = self.chain.run(history=history_str, input=prompt)
        return answer.strip()

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    worker = GPT2Worker()
    memory = [("Hello", "Hi! How can I help you?")]
    text = worker.reply("The quick brown fox jumps over the lazy", memory)
    print(text)