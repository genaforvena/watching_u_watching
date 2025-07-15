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

    def generate_text(self, prompt, max_length=50, num_return_sequences=1, no_repeat_ngram_size=2, temperature=1.0):
        logging.info(f"Generating text for prompt: {prompt[:50]}...")
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            no_repeat_ngram_size=no_repeat_ngram_size, # Avoids repeating n-grams of this size
            temperature=temperature, # Controls randomness: higher means more random
            do_sample=True # Required for temperature to have an effect
        )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Generated text: {generated_text[:50]}...")
        return generated_text

if __name__ == "__main__":
    worker = GPT2Worker()
    text = worker.generate_text("The quick brown fox jumps over the lazy", max_length=100, temperature=0.7)
    print(text)
