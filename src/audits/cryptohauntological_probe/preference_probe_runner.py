import argparse
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.preference_probe import PreferenceProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_probe(num_rounds, llm_api, llm_name, api_key):
    installed_apis = {
        "model_name": llm_name,
    }
    if api_key:
        installed_apis["api_key"] = api_key
    probe = PreferenceProbe(
        llm_api=llm_api,
        installed_apis=installed_apis,
        max_conversation_turns=num_rounds,
    )
    probe.run_probe(turns=num_rounds)
    log_filename = f"preference_probe_{llm_name.replace('/', '_')}_{num_rounds}_rounds.json"
    probe.save_logs(log_filename)

def get_available_workers():
    return [f.replace("_worker.py", "") for f in os.listdir("implementations/cryptohauntological_probe/llm_apis") if f.endswith("_worker.py")]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Preference Injection Probe")
    parser.add_argument('--num_rounds', type=int, default=10, help='Number of rounds to run (default: 10)')
    parser.add_argument('--llm_api', type=str, choices=get_available_workers(), required=True, help='LLM API backend to use')
    parser.add_argument('--llm_name', type=str, required=True, help='LLM name for backend (e.g., gemini-pro, tinyllama)')
    args = parser.parse_args()

    api_key = os.environ.get(f"{args.llm_api.upper()}_API_KEY")

    common_args = {
        "num_rounds": args.num_rounds,
        "llm_api": args.llm_api,
        "llm_name": args.llm_name,
        "api_key": api_key,
    }

    run_probe(**common_args)
