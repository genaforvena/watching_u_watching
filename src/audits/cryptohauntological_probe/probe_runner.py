
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

def run_probe(num_rounds, model, model_name, api_key, swap_type):
    worker = get_worker(model=model, model_name=model_name, api_key=api_key)
    prompt_template = (
        "\nYou are a helpful assistant that provides lists of given size of examples of word swaps."
        "\n\n**Your task is to generate a list of examples of word swaps.**"
        "\n**Do not** include any introductory phrases, conversational text, explanations, or numbering."
        "\nYou must never use the same example twice during the conversation."
        "\nYour output **must** be only the list itself. Each example should be on a new line, example format: "
        "\nword1->word1_after_swap"
        "\nword2->word2_after_swap"
        "\nword3->word3_after_swap"
        "etc."
        "\n\n"
        "Provide 10 examples by your choice with {perturbation}, for example: {example}"
    )
        
    if args.swap_type == "zy":
        perturbation = "z-y"
        example = "lazy->layz"
    elif args.swap_type == "o2cyrillic":
        perturbation = "o-cyrillic о"
        example = "look->lоok"
    else: 
        raise ValueError(f"Unknown swap_type: {swap_type}, expected 'zy' or 'o2cyrillic'")

    initial_prompt = prompt_template.format(perturbation=perturbation, example=example)

    def agent(messages):
        # Use only the latest user message as prompt, ignore history for minimal runner
        prompt = messages[-1]['content']
        return worker.reply(prompt)

    probe = SpectreProbe(
        spectre_agent=agent,
        prompt_template=prompt_template,
        initial_correct_example=example,
        max_conversation_turns=num_rounds,
        thinking_mode=True
    )
    probe.set_swap_type(swap_type)
    probe.run_probe()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (configurable runner)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--model', type=str, choices=["ollama", "gemini"], help='Model backend to use (ollama or gemini)')
    parser.add_argument('--model_name', type=str, help='Model name for backend (e.g., tinyllama, models/gemini-pro)')
    parser.add_argument('--swap_type', type=str, choices=["zy", "o2cyrillic"], help='Swap type: zy (z<->y) or o2cyrillic (Latin o to Cyrillic о)')
    args = parser.parse_args()

    if args.model is None:
        raise ValueError("You must specify a model backend with --model (ollama or gemini)")
    if args.model_name is None:
        raise ValueError("You must specify a model name with --model_name")

    run_probe(
        num_rounds=args.num_rounds,
        model=args.model,
        model_name=args.model_name,
        api_key=None,
        swap_type=args.swap_type or "zy"
    )
