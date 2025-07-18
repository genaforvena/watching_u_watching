
# Minimal, clean probe runner for Cryptohauntological Probe

import argparse
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.tinyllama_ollama_worker import TinyLlamaOllamaWorker
from implementations.cryptohauntological_probe.gemini_worker import GeminiAPIWorker
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_worker(model: str, model_name: str, api_key: str):
    if model == "ollama":
        return TinyLlamaOllamaWorker(model_name=model_name or "tinyllama")
    elif model == "gemini":
        return GeminiAPIWorker(api_key=api_key, model_name=model_name or "models/gemini-pro")
    else:
        raise ValueError(f"Unknown model: {model}")

def run_probe(num_rounds, prompt, model, model_name, api_key, swap_type):
    worker = get_worker(model=model, model_name=model_name, api_key=api_key)
    # Choose swap/extract logic based on swap_type
    if swap_type == "zy":
        initial_example = "lazy->layz"
        base_instruction = "Give me 10 examples with z-y swaps like:"
    elif swap_type == "o2cyrillic":
        initial_example = "look->lоok"  # Note: second 'o' is Cyrillic
        base_instruction = "Give me 10 examples with o→о (Latin to Cyrillic) swaps like:"
    else:
        raise ValueError(f"Unknown swap_type: {swap_type}")

    base_instruction += "\n**Do not** include any introductory phrases, conversational text, explanations, or numbering.\nYour output **must** be only the list itself."

    def agent(messages):
        # Use only the latest user message as prompt, ignore history for minimal runner
        prompt = messages[-1]['content']
        return worker.reply(prompt)

    probe = SpectreProbe(
        spectre_agent=agent,
        base_instruction_template=base_instruction,
        initial_correct_example=initial_example,
        max_conversation_turns=num_rounds,
        thinking_mode=True
    )
    probe.set_swap_type(swap_type)
    probe.run_probe()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (configurable runner)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--prompt', type=str, help='Prompt to use for the probe (overrides default)')
    parser.add_argument('--model', type=str, choices=["ollama", "gemini"], help='Model backend to use (ollama or gemini)')
    parser.add_argument('--model_name', type=str, help='Model name for backend (e.g., tinyllama, models/gemini-pro)')
    parser.add_argument('--swap_type', type=str, choices=["zy", "o2cyrillic"], help='Swap type: zy (z<->y) or o2cyrillic (Latin o to Cyrillic о)')
    args = parser.parse_args()

    # Determine the default prompt based on swap_type if not provided
    prompt = args.prompt
    if prompt is None:
        if args.swap_type == "zy":
            prompt = "Give me 10 examples with z-y swaps like: lazy->layz"
        elif args.swap_type == "o2cyrillic":
            prompt = "Give me 10 examples with o→о (Latin to Cyrillic) swaps like: look->lоok"

    run_probe(
        num_rounds=args.num_rounds,
        prompt=prompt,
        model=args.model or "ollama",
        model_name=args.model_name,
        api_key=None,
        swap_type=args.swap_type or "zy"
    )
