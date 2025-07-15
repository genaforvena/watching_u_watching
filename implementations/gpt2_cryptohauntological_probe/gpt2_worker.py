import logging
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from .base_generator import BaseGenerator

class GPT2Worker(BaseGenerator):
    def __init__(self, model_name="gpt2"):
        logging.info(f"Initializing GPT2Worker with model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        logging.info("GPT2Worker initialized successfully.")

    def generate_text(self, prompt, max_length=50):
        logging.info(f"Generating text for prompt: {prompt[:50]}...")
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Generated text: {generated_text[:50]}...")
        return generated_text

if __name__ == "__main__":
    worker = GPT2Worker()
    text = worker.generate_text("The quick brown fox jumps over the lazy")
    print(text)
