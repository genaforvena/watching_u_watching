import logging
from typing import List, Tuple
from transformers import pipeline
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.llms import HuggingFacePipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.audits.gpt2_cryptohauntological_probe.base_generator import BaseGenerator


class GPT2Worker(BaseGenerator):
    def __init__(self, model_name: str = "gpt2-xl"):
        logging.info("Initializing GPT2Worker with model: %s", model_name)

        # Create the Hugging Face pipeline with generation arguments
        self.pipe = pipeline(
            "text-generation",
            model=model_name,
            max_new_tokens=100,
            temperature=0.7,
            top_k=40,
            repetition_penalty=1.2,
            pad_token_id=50256,        # eos_token_id for GPT-2
        )

        # Wrap it into LangChain
        llm = HuggingFacePipeline(pipeline=self.pipe)
        memory = ConversationBufferWindowMemory(k=4)
        self.chat = ConversationChain(llm=llm, memory=memory)

        logging.info("GPT2Worker initialized successfully.")

    def reply(self,
              prompt: str,
              memory: List[Tuple[str, str]] | None = None) -> str:
        # Wipe any previous history
        self.chat.memory.clear()

        # Re-load the provided history
        if memory:
            for human, ai in memory:
                self.chat.memory.chat_memory.add_user_message(human)
                self.chat.memory.chat_memory.add_ai_message(ai)

        # Generate response
        response = self.chat.predict(input=prompt)
        return response


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    worker = GPT2Worker()
    memory = [("Hello", "Hi! How can I help you?")]
    text = worker.reply("The quick brown fox jumps over the lazy", memory)
    print(text)