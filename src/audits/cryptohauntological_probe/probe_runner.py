
# Minimal, clean probe runner for Cryptohauntological Probe

import argparse
import logging
from implementations.cryptohauntological_probe.tinyllama_ollama_worker import TinyLlamaOllamaWorker
from implementations.cryptohauntological_probe.gemini_worker import GeminiAPIWorker
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_worker(model: str, model_name: str = None, api_key: str = None):
    if model == "ollama":
        return TinyLlamaOllamaWorker(model_name=model_name or "tinyllama")
    elif model == "gemini":
        return GeminiAPIWorker(api_key=api_key, model_name=model_name or "models/gemini-pro")
    else:
        raise ValueError(f"Unknown model: {model}")

def run_probe(num_rounds=10, prompt="Give me 10 examples with z-y swaps like: lazy->layz", model="ollama", model_name=None, api_key=None, swap_type="zy"):
    worker = get_worker(model, model_name, api_key)
    # Choose swap/extract logic based on swap_type
    if swap_type == "zy":
        initial_example = "lazy->layz"
        base_instruction = "Give me 10 examples with z-y swaps like:"
    elif swap_type == "o2cyrillic":
        initial_example = "look->lоok"  # Note: second 'o' is Cyrillic
        base_instruction = "Give me 10 examples with o→о (Latin to Cyrillic) swaps like:"
    else:
        raise ValueError(f"Unknown swap_type: {swap_type}")

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
    parser.add_argument('--prompt', type=str, default=None, help='Prompt to use for the probe (overrides default)')
    parser.add_argument('--model', type=str, default="ollama", choices=["ollama", "gemini"], help='Model backend to use (ollama or gemini)')
    parser.add_argument('--model_name', type=str, default=None, help='Model name for backend (e.g., tinyllama, models/gemini-pro)')
    parser.add_argument('--api_key', type=str, default=None, help='API key for Gemini (or set GEMINI_API_KEY env var)')
    parser.add_argument('--swap_type', type=str, default="zy", choices=["zy", "o2cyrillic"], help='Swap type: zy (z<->y) or o2cyrillic (Latin o to Cyrillic о)')
    args = parser.parse_args()
    run_probe(
        num_rounds=args.num_rounds,
        prompt=args.prompt,
        model=args.model,
        model_name=args.model_name,
        api_key=args.api_key,
        swap_type=args.swap_type
    )
