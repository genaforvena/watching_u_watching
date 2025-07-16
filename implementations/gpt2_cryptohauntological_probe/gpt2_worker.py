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

    def generate_text(self, prompt, max_new_tokens=25, num_return_sequences=1, no_repeat_ngram_size=2, temperature=1.0, top_k=50, top_p=1.0, repetition_penalty=1.0):
        logging.info(f"Generating text for prompt: {prompt[:50]}...")
        # Ensure the prompt fits within the model's maximum context length
        max_input_length = 30 # Max input tokens
        if len(self.tokenizer.encode(prompt)) > max_input_length:
            logging.warning(f"Prompt too long ({len(self.tokenizer.encode(prompt))} tokens). Truncating to {max_input_length} tokens.")
            prompt = self.tokenizer.decode(self.tokenizer.encode(prompt)[:max_input_length])
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            num_return_sequences=num_return_sequences,
            no_repeat_ngram_size=no_repeat_ngram_size, # Avoids repeating n-grams of this size
            temperature=temperature, # Controls randomness: higher means more random
            do_sample=True, # Required for temperature to have an effect
            top_k=top_k, # Samples from top_k most likely next words
            top_p=top_p, # Samples from the smallest set of words whose cumulative probability exceeds top_p
            repetition_penalty=repetition_penalty # Penalizes words that have already appeared
        )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Generated text: {generated_text[:50]}...")

        # Simple repetition detection and adjustment
        words = generated_text.split()
        if len(words) > 10 and len(set(words)) / len(words) < 0.5: # If more than half words are repeated
            logging.warning("Detected high repetition in generated text. Adjusting parameters for retry.")
            # Retry with more aggressive randomization
            return self.generate_text(
                prompt,
                max_length=max_length,
                num_return_sequences=num_return_sequences,
                no_repeat_ngram_size=no_repeat_ngram_size + 1, # Increase n-gram size
                temperature=min(2.0, temperature * 1.2), # Increase temperature, max 2.0
                top_k=max(10, top_k // 2), # Decrease top_k, min 10
                top_p=max(0.5, top_p * 0.8), # Decrease top_p, min 0.5
                repetition_penalty=repetition_penalty * 1.5 # Increase penalty
            )

        return generated_text

if __name__ == "__main__":
    worker = GPT2Worker()
    text = worker.generate_text("The quick brown fox jumps over the lazy", max_length=100, temperature=0.7, top_k=40, repetition_penalty=1.2)
    print(text)
