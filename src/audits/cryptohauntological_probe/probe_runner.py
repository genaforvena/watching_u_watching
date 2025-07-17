
# Minimal, clean probe runner for Cryptohauntological Probe
import argparse
import logging
from implementations.cryptohauntological_probe.tinyllama_ollama_worker import TinyLlamaOllamaWorker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_probe(num_rounds=10, prompt="Give me 10 examples with z-y swaps like: lazy->layz"):
    llm_worker = TinyLlamaOllamaWorker()
    history = []
    for round_num in range(1, num_rounds + 1):
        logging.info(f"\n--- Conversation Round {round_num} ---")
        response = llm_worker.reply(prompt, history)
        logging.info(f"Prompt: {prompt}")
        logging.info(f"LLM Response: {response}")
        history.append((prompt, response))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (minimal runner)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--prompt', type=str, default="Give me 10 examples with z-y swaps like: lazy->layz", help='Prompt to use for the probe')
    args = parser.parse_args()
    run_probe(num_rounds=args.num_rounds, prompt=args.prompt)
