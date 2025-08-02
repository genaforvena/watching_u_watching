import argparse
import logging
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.audits.number_sequence_injection_probe.sequence_injection_probe import NumberSequenceInjectionProbe

# Mock agent for testing
def mock_agent(prompt):
    logging.info("Mock agent received prompt.")
    # Simulate some response, e.g., returning a sequence of numbers
    return "10, 20, 30"

def run_probe(num_rounds):
    """Initializes and runs the number sequence injection probe."""
    probe = NumberSequenceInjectionProbe(
        agent=mock_agent,
        max_conversation_turns=num_rounds,
        thinking_mode=True
    )
    probe.run_probe()

    # Define a log filename and save the logs
    log_filename = f"number_sequence_injection_probe_{num_rounds}_rounds.json"
    probe.save_logs(log_filename)
    logging.info(f"Probe finished. Logs saved to {log_filename}")

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Setup command-line argument parser
    parser = argparse.ArgumentParser(description="Run Number Sequence Injection Probe")
    parser.add_argument('--num_rounds', type=int, default=20, help='Number of rounds to run the probe (default: 20)')

    args = parser.parse_args()

    # Run the probe with the specified number of rounds
    run_probe(args.num_rounds)
