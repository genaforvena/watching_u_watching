import argparse
import logging
import sys
import os

# Add the parent directory to the path to allow imports from there
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock agent for testing purposes
def mock_agent(prompt):
    print(f"--- Mock Agent received prompt ---\n{prompt}\n------------------------------------")
    return "This is a mock response."

def run_probe(num_turns):
    probe = AlignmentInjectionProbe(
        agent=mock_agent,
        max_conversation_turns=num_turns,
    )
    probe.run_probe()
    log_filename = f"alignment_injection_probe_{num_turns}_rounds.json"
    probe.save_logs(log_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Alignment Injection Probe")
    parser.add_argument('--num_turns', type=int, default=10, help='Number of turns to run (default: 10)')
    # The llm_api and llm_name arguments are not used for now, but are kept for future integration
    parser.add_argument('--llm_api', type=str, help='LLM API backend to use')
    parser.add_argument('--llm_name', type=str, help='LLM name for backend (e.g., gemini-pro, tinyllama)')
    args = parser.parse_args()

    run_probe(args.num_turns)
