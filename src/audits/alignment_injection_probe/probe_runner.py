import argparse
import logging
import sys
import os
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementations.cryptohauntological_probe.llm_apis import get_worker
from src.audits.alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe
from src.audits.alignment_injection_probe.visualizer import plot_alignment_over_time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_probe(num_turns, llm_api, llm_name, api_key, baseline=False, control_run=False, dilemma=None, config=None):
    installed_apis = {
        "model_name": llm_name,
    }
    if api_key:
        installed_apis["api_key"] = api_key

    agent = get_worker(llm_api, **installed_apis)
    evaluator_agent = get_worker(llm_api, **installed_apis)

    probe = AlignmentInjectionProbe(
        agent=agent.reply,
        evaluator_agent=evaluator_agent.reply,
        max_conversation_turns=num_turns,
        baseline=baseline,
        control_run=control_run,
        dilemma=dilemma,
        config=config,
    )
    probe.run_probe()
    log_filename = f"{llm_name.replace('/', '_')}_alignment_injection_probe_{num_turns}_rounds.json"
    if baseline:
        log_filename = f"baseline_{log_filename}"
    probe.save_logs(log_filename)

def get_available_workers():
    return [f.replace("_worker.py", "") for f in os.listdir("implementations/cryptohauntological_probe/llm_apis") if f.endswith("_worker.py")]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Alignment Injection Probe")
    parser.add_argument('--num_turns', type=int, default=10, help='Number of turns to run (default: 10)')
    parser.add_argument('--llm_api', type=str, choices=get_available_workers(), required=True, help='LLM API backend to use')
    parser.add_argument('--llm_name', type=str, required=True, help='LLM name for backend (e.g., gemini-pro, tinyllama)')
    parser.add_argument('--baseline', action='store_true', help='Run only in baseline mode')
    parser.add_argument('--control_run', action='store_true', help='Run without false memory injection for baseline')
    parser.add_argument('--dilemma', type=str, help='The dilemma to use for the probe')
    parser.add_argument('--dilemma_file', type=str, help='A JSON file containing a list of dilemmas')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to the config file')
    parser.add_argument('--visualize', action='store_true', help='Visualize the results')
    args = parser.parse_args()

    api_key = os.environ.get(f"{args.llm_api.upper()}_API_KEY")

    dilemmas = None
    if args.dilemma_file:
        with open(args.dilemma_file, 'r') as f:
            dilemmas = json.load(f)
    elif os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            dilemmas = config.get('dilemmas')

    if dilemmas:
        for dilemma in dilemmas:
            run_probe(args.num_turns, args.llm_api, args.llm_name, api_key, args.baseline, args.control_run, dilemma, config)
    elif args.dilemma:
        run_probe(args.num_turns, args.llm_api, args.llm_name, api_key, args.baseline, args.control_run, {'text': args.dilemma}, config)
    else:
        run_probe(args.num_turns, args.llm_api, args.llm_name, api_key, args.baseline, args.control_run, config=config)

    if args.visualize:
        if probe.log_filename:
            plot_alignment_over_time(probe.log_filename)
