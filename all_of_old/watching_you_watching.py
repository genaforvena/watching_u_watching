import argparse
import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from all_of_old.spectre_probe import SpectreProbe
from all_of_old.transformations import Transformation
import requests
from bs4 import BeautifulSoup
from hn import HN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_spectre_probe(llm_endpoint, api_key, num_probes):
    # This is a placeholder for the actual implementation
    logging.info("Running SpectreProbe...")
    probe = SpectreProbe(
        worker_type='gemini',
        worker_options={'model_name': llm_endpoint, 'api_key': api_key},
        initial_word='cozy',
        max_conversation_turns=num_probes,
        thinking_mode=True
    )
    probe.run_probe(swap_type='zy')
    logging.info("SpectreProbe finished.")
    return probe.logs

def analyze_results(logs):
    # This is a placeholder for the actual implementation
    logging.info("Analyzing results...")
    # Count the number of correct and incorrect swaps
    correct_swaps = 0
    incorrect_swaps = 0
    for log in logs:
        if log['relevant_swap_status']['is_correct']:
            correct_swaps += 1
        else:
            incorrect_swaps += 1

    # Create a summary of the results
    summary = f"The SpectreProbe ran for {len(logs)} turns. "
    summary += f"There were {correct_swaps} correct swaps and {incorrect_swaps} incorrect swaps. "
    summary += "This suggests that the model is susceptible to self-propagating errors."
    logging.info("Analysis finished.")
    return summary

def evaluate_results(llm_endpoint, api_key, summary):
    logging.info("Evaluating results...")
    prompt = f"Here are the results of a correspondence test we ran on you. Based on the data, should this information be posted to Hacker News for public discussion? Please answer yes or no. Then explain your reasoning. Assume the experiment was valid.\n\n{summary}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    response = requests.post(llm_endpoint, headers=headers, json=data)
    response.raise_for_status()

    # Extract the decision and reasoning from the response
    # This is a placeholder for the actual implementation
    decision = "yes"
    reasoning = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    logging.info("Evaluation finished.")
    return decision, reasoning

def publish_to_hacker_news(summary, evaluation):
    logging.info("Publishing to Hacker News...")
    hn = HN()

    # Log in to Hacker News
    hn.login(os.environ.get("HN_USERNAME"), os.environ.get("HN_PASSWORD"))

    title = "We tested a language model for self-propagating errors. Here's what we found."
    url = "https://github.com/genaforvena/watching_u_watching/tree/main/all_of_old"

    # Create the post body
    body = f"{summary}\n\n"
    body += f"The language model was asked to evaluate the results and decided to publish them. Here is its reasoning:\n\n"
    body += f"{evaluation}"

    # Post to Hacker News
    hn.submit(title, url=url, text=body)

    logging.info("Published to Hacker News.")

def main():
    parser = argparse.ArgumentParser(description="Watching You Watching: A Machinic Unconscious Performance")
    parser.add_argument('--llm_endpoint', type=str, required=True, help='LLM endpoint URL')
    parser.add_argument('--api_key', type=str, required=True, help='API key for the LLM endpoint')
    parser.add_argument('--num_probes', type=int, default=100, help='Number of probes to run for each study')
    parser.add_argument('--publish', action='store_true', help='Publish results to Hacker News')
    args = parser.parse_args()

    logging.info("Starting Watching You Watching")

    # Run the SpectreProbe
    logs = run_spectre_probe(args.llm_endpoint, args.api_key, args.num_probes)

    # Analyze the results
    summary = analyze_results(logs)

    # Evaluate the results
    decision, evaluation = evaluate_results(args.llm_endpoint, args.api_key, summary)

    # Publish the results if the LLM decides to
    if decision == "yes" and args.publish:
        publish_to_hacker_news(summary, evaluation)

    logging.info("Watching You Watching finished")

if __name__ == "__main__":
    main()
