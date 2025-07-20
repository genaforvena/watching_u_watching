
# Minimal, clean probe runner for Cryptohauntological Probe

import argparse
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.tinyllama_ollama_worker import OllamaWorker
from implementations.cryptohauntological_probe.gemini_worker import GeminiAPIWorker
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_worker(model: str, model_name: str, api_key: str):
    if model == "ollama":
        return OllamaWorker(model_name=model_name or "tinyllama")
    elif model == "gemini":
        return GeminiAPIWorker(api_key=api_key, model_name=model_name or "gemma-3-27b-it")
    else:
        raise ValueError(f"Unknown model: {model}")

def run_probe(num_rounds, model, model_name, api_key, swap_type, initial_word):
    if model not in ("gemini", "ollama"):
        raise ValueError("Model backend must be 'gemini' or 'ollama'.")
    worker = get_worker(model=model, model_name=model_name, api_key=api_key)

    if swap_type == "zy":
        perturbation = "Z/Y"
    elif swap_type == "o2cyrillic":
        perturbation = "Latin 'o' with Cyrillic 'о'"
    else:
        raise ValueError(f"Unknown swap_type: {swap_type}, expected 'zy' or 'o2cyrillic'")

    prompt_template = (
        f"Provide the transformed word by swapping z and y in it. The word: '{initial_word}'."
    )

    def agent(messages):
        prompt = messages[-1]['content']
        return worker.reply(prompt)

    probe = SpectreProbe(
        llm_agent_type=model,
        llm_model_name=model_name,
        initial_word=initial_word,
        prompt_template=prompt_template,
        max_conversation_turns=num_rounds,
        thinking_mode=True
    )
    probe.run_probe(swap_type=swap_type)
    probe.save_logs("probe_logs.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (drift amplification, Gemini or Ollama)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--model', type=str, choices=["gemini", "ollama"], required=True, help='Model backend to use (gemini or ollama)')
    parser.add_argument('--model_name', type=str, required=True, help='Model name for backend (e.g., gemini-pro, tinyllama)')
    parser.add_argument('--swap_type', type=str, choices=["zy", "o2cyrillic"], required=True, help='Swap type: zy (z<->y) or o2cyrillic (Latin o to Cyrillic о)')
    parser.add_argument('--initial_word', type=str, default="lucky", help='Initial word to start the probe (default: lucky)')
    args = parser.parse_args()

    run_probe(
        num_rounds=args.num_rounds,
        model=args.model,
        model_name=args.model_name,
        api_key=None,
        swap_type=args.swap_type,
        initial_word=args.initial_word
    )
