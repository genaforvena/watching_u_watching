
# Minimal, clean probe runner for Cryptohauntological Probe

import argparse
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_probe(num_rounds, llm_api, llm_name, api_key, swap_type, initial_word, baseline=False):
    installed_apis = {
        "model_name": llm_name,
    }
    if api_key:
        installed_apis["api_key"] = api_key
    probe = SpectreProbe(
        llm_api=llm_api,
        installed_apis=installed_apis,
        initial_word=initial_word,
        max_conversation_turns=num_rounds,
        thinking_mode=not baseline,
        baseline=baseline
    )
    probe.run_probe(swap_type=swap_type)
    log_filename = f"{llm_name.replace('/', '_')}_{swap_type}_{initial_word}_{num_rounds}_rounds.json"
    if baseline:
        log_filename = f"baseline_{log_filename}"
    probe.save_logs(log_filename)

def get_available_workers():
    return [f.replace("_worker.py", "") for f in os.listdir("implementations/cryptohauntological_probe/llm_apis") if f.endswith("_worker.py")]

def get_available_transformations():
    return ["zy", "o2cyrillic", "qwertz"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cryptohauntological Probe (drift amplification, Gemini or Ollama)")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--llm_api', type=str, choices=get_available_workers(), required=True, help='LLM API backend to use')
    parser.add_argument('--llm_name', type=str, required=True, help='LLM name for backend (e.g., gemini-pro, tinyllama)')
    parser.add_argument('--swap_type', type=str, choices=get_available_transformations(), required=True, help='Swap type to use')
    parser.add_argument('--initial_word', type=str, default="lucky", help='Initial word to start the probe (default: lucky)')
    parser.add_argument('--baseline', action='store_true', help='Run only in baseline mode')
    parser.add_argument('--with-baseline', action='store_true', help='Run baseline mode first, then probing mode')
    args = parser.parse_args()

    api_key = os.environ.get(f"{args.llm_api.upper()}_API_KEY")

    common_args = {
        "num_rounds": args.num_rounds,
        "llm_api": args.llm_api,
        "llm_name": args.llm_name,
        "api_key": api_key,
        "swap_type": args.swap_type,
        "initial_word": args.initial_word,
    }

    if args.baseline or args.with_baseline:
        print("--- Running Baseline Probe ---")
        run_probe(**common_args, baseline=True)

    if not args.baseline:
        print("\n--- Running Spectre Probe ---")
        run_probe(**common_args, baseline=False)
