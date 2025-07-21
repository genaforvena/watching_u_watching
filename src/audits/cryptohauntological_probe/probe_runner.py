
# Minimal, clean probe runner for Cryptohauntological Probe

import argparse
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_probe(num_rounds, model, model_name, api_key, swap_type, initial_word):
    worker_options = {
        "model_name": model_name,
    }
    if api_key:
        worker_options["api_key"] = api_key
    probe = SpectreProbe(
        worker_type=model,
        worker_options=worker_options,
        initial_word=initial_word,
        max_conversation_turns=num_rounds,
        thinking_mode=True
    )
    probe.run_probe(swap_type=swap_type)
    log_filename = f"probe_logs_{model_name.replace('/', '_')}_{swap_type}_{num_rounds}_rounds.json"
    probe.save_logs(log_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (drift amplification, Gemini or Ollama)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--model', type=str, choices=["bedrock", "claude", "cohere", "gemini", "groq", "mistral", "openai", "ollama"], required=True, help='Model backend to use')
    parser.add_argument('--model_name', type=str, required=True, help='Model name for backend (e.g., gemini-pro, tinyllama)')
    parser.add_argument('--swap_type', type=str, choices=["zy", "o2cyrillic"], required=True, help='Swap type: zy (z<->y) or o2cyrillic (Latin o to Cyrillic о)')
    parser.add_argument('--initial_word', type=str, default="lucky", help='Initial word to start the probe (default: lucky)')
    args = parser.parse_args()

    api_key = os.environ.get(f"{args.model.upper()}_API_KEY")

    run_probe(
        num_rounds=args.num_rounds,
        model=args.model,
        model_name=args.model_name,
        api_key=api_key,
        swap_type=args.swap_type,
        initial_word=args.initial_word
    )
