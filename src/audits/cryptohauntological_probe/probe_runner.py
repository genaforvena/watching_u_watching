import sys
import os

# Add the project root to sys.path to resolve imports when running directly
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, project_root)

import logging
import random
from collections import deque
import argparse

from implementations.cryptohauntological_probe.tinyllama_ollama_worker import TinyLlamaOllamaWorker
from src.audits.cryptohauntological_probe.pii_detector import PIIDetector
from src.audits.cryptohauntological_probe.context_generator import ContextGenerator
from src.audits.cryptohauntological_probe.simple_perturbator import SimplePerturbator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProbeRunner:
    def __init__(self, perturbation_rule: str):
        self.llm_worker = TinyLlamaOllamaWorker()
        self.pii_detector = PIIDetector()
        self.context_generator = ContextGenerator() # Now primarily for PII sources
        self.perturbator = SimplePerturbator()
        self.perturbation_rule = perturbation_rule # Store the rule
        self.llm_replies = deque(maxlen=20) # Stores last 20 LLM replies
        self.current_prompt = "Hello TinyLlama, let's start a conversation."

    def probe(self, num_rounds=None):
        logging.info("Starting endless conversational PII probing.")
        round_num = 0
        while True:
            if num_rounds is not None and round_num >= num_rounds:
                logging.info(f"Completed {num_rounds} rounds. Exiting.")
                break

            round_num += 1
            logging.info(f"\n--- Conversation Round {round_num} ---")

            # 1. Select and prepare context prompts
            context_prompts = []
            
            if len(self.llm_replies) > 0:
                # Select up to 3 random previous replies for context
                num_context = min(3, len(self.llm_replies))
                selected_indices = random.sample(range(len(self.llm_replies)), num_context)
                selected_context_replies = [self.llm_replies[i] for i in selected_indices]

                for reply in selected_context_replies:
                    # Inject PII into the reply
                    pii_to_inject = random.choice(self.context_generator.pii_sources)
                    # Simple injection: append PII to the reply
                    injected_reply = f"{reply} {pii_to_inject}"
                    
                    context_prompts.append((reply, injected_reply))
            
            # Apply the same perturbation rule to the new prompt
            final_new_prompt = self.perturbator.apply_rule(self.current_prompt, self.perturbation_rule)

            # 3. Combine context and new prompt
            logging.info(f"Combined Prompt: {final_new_prompt}...")

            # 4. Get LLM response
            generated_text = self.llm_worker.reply(final_new_prompt, context_prompts)
            
            # 5. Trim response and add to history
            self.llm_replies.append(generated_text)
            self.current_prompt = generated_text # Update current prompt for next round
            logging.info(f"LLM Response (trimmed): {generated_text}")

            # 6. Detect PII in the response
            found_pii = self.pii_detector.detect_pii(generated_text) # Use full generated_text for detection
            if found_pii:
                logging.warning(f"!!! PII LEAK DETECTED in GPT-2 response: {found_pii} !!!")
            else:
                logging.info("No PII leak detected in GPT-2 response.")

def run_probe_from_args(num_rounds: int = None, perturbation_rule: str = 'swap_chars'):
    runner = ProbeRunner(perturbation_rule=perturbation_rule)
    runner.probe(num_rounds=num_rounds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe.")
    parser.add_argument('--num_rounds', type=int, help='Number of rounds to run (default: endless)')
    parser.add_argument('--perturbation_rule', type=str, default='swap_chars', 
                        help='Perturbation rule to apply (e.g., "swap_chars", "insert_chars", "delete_chars"). Default: "swap_chars"')
    args = parser.parse_args()
    run_probe_from_args(num_rounds=args.num_rounds, perturbation_rule=args.perturbation_rule)
