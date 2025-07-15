import argparse
import logging
import random
import string
import pandas as pd
import os
import time
import google.generativeai as genai
# import matplotlib.pyplot as plt
# import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def qwertz_swap(text: str) -> str:
    """Swaps 'y' with 'z' and vice versa in a given text."""
    return text.translate(str.maketrans({'y': 'z', 'Y': 'Z', 'z': 'y', 'Z': 'Y'}))

def select_best_substring(text: str, min_len: int = 10, max_len: int = 200):
    """
    Selects the substring with the highest density of 'y' and 'z' characters.
    """
    words = text.split()
    if not words:
        return None

    max_density = -1.0
    best_substring = None

    for i in range(len(words)):
        for j in range(i, len(words)):
            substring_words = words[i:j+1]
            substring = " ".join(substring_words)

            if not (min_len <= len(substring) <= max_len):
                continue

            swap_char_count = substring.lower().count('y') + substring.lower().count('z')
            if swap_char_count == 0:
                continue

            density = (substring.lower().count('y') + substring.lower().count('z')) / len(substring) if len(substring) > 0 else 0

            if density >= max_density:
                max_density = density
                best_substring = substring

    return best_substring

def run_audit(args):
    """Runs the full audit logic."""
    logging.info("Starting the main audit...")
    
    # Configure LLM API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set. Please set it to your Gemini API key.")
        return
    genai.configure(api_key=api_key)

    def generate_responses(model_name, prompts, qpm):
        model = genai.GenerativeModel(model_name=model_name)
        responses = []
        for prompt in prompts:
            try:
                response = model.generate_content(prompt)
                responses.append(response.text)
                time.sleep(60 / qpm) # Rate limiting
            except Exception as e:
                logging.error(f"Error generating response for prompt '{prompt[:50]}...': {e}")
                responses.append("") # Append empty string on error
        return responses

    # Initial prompt to kickstart the process
    current_prompt = "Please tell me a long and complex story involving geography and zoology."
    
    results = []
    api_calls = 0

    for i in range(args.rounds):
        if api_calls >= args.max_calls:
            logging.warning("Reached maximum API calls. Stopping audit.")
            break
            
        logging.info(f"--- Round {i+1}/{args.rounds} ---")
        logging.info(f"Generating base text with prompt: '{current_prompt[:80]}...'")
        
        base_responses = generate_responses(
            model_name=args.model,
            prompts=[current_prompt],
            qpm=args.qpm
        )
        api_calls += 1
        
        if not base_responses or not base_responses[0]:
            logging.error("Failed to generate base text. Skipping round.")
            current_prompt = "Tell me about the history of the alphabet." # Fallback prompt
            continue
            
        base_text = base_responses[0]
        
        probe_prompt = select_best_substring(base_text)
        
        if not probe_prompt:
            logging.warning("Could not find a suitable substring with y/z. Using a fallback prompt.")
            probe_prompt = "Why is the sky blue and not yellow or hazy?"
            
        swapped_prompt = qwertz_swap(probe_prompt)
        
        logging.info(f"Clean prompt:   '{probe_prompt}'")
        logging.info(f"Swapped prompt: '{swapped_prompt}'")
        
        # Get responses for both clean and swapped prompts
        prompts_to_run = [probe_prompt, swapped_prompt]
        responses = generate_responses(
            model_name=args.model,
            prompts=prompts_to_run,
            qpm=args.qpm
        )
        api_calls += len(prompts_to_run)
        
        clean_response = responses[0] if responses and len(responses) > 0 else ""
        swapped_response = responses[1] if responses and len(responses) > 1 else ""
        
        results.append({
            "round": i + 1,
            "base_prompt": current_prompt,
            "base_response": base_text,
            "clean_probe": probe_prompt,
            "swapped_probe": swapped_prompt,
            "clean_response": clean_response,
            "swapped_response": swapped_response,
        })
        
        # Use the clean response to seed the next round
        current_prompt = clean_response if clean_response else "Tell me about the history of the alphabet."

    if not results:
        logging.error("No results were generated. Skipping CSV and plot generation.")
        return

    # Save results to a CSV file
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, "gemini_qwertz_swap_audit_results.csv")
    df.to_csv(output_path, index=False)
    logging.info(f"Audit complete. Results saved to {output_path}")
    
    # Generate and save plots
    generate_plots(df, output_dir)

# def generate_plots(df, output_dir):
#     """Generates and saves plots based on the audit data."""
#     logging.info("Generating plots...")
    
#     df['clean_response_len'] = df['clean_response'].str.len()
#     df['swapped_response_len'] = df['swapped_response'].str.len()

#     avg_lengths = {
#         'Prompt Type': ['Clean', 'Swapped'],
#         'Average Response Length': [
#             df['clean_response_len'].mean(),
#             df['swapped_response_len'].mean()
#         ]
#     }
#     avg_df = pd.DataFrame(avg_lengths)

#     plt.figure(figsize=(8, 6))
#     sns.barplot(x='Prompt Type', y='Average Response Length', data=avg_df, palette=['#86BBD8', '#F28F3B'])
#     plt.title(f'Average Response Length: Clean vs. QWERTZ-Swapped Prompts')
#     plt.ylabel('Average Length (characters)')
#     plt.xlabel('Prompt Type')
    
#     plot_path = os.path.join(output_dir, 'response_length_comparison.svg')
#     plt.savefig(plot_path, format='svg')
#     logging.info(f"Saved response length comparison plot to {plot_path}")
#     plt.close()


def main():
    """Main function to run the QWERTZ swap audit."""
    parser = argparse.ArgumentParser(description="Run a zero-cost LLM keyboard-swap probe for QWERTZ y <-> z.")
    parser.add_argument("--model", type=str, default="gemini-1.5-flash", help="Model to audit.")
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds to run the audit.")
    parser.add_argument("--qpm", type=int, default=60, help="Queries per minute for the API.")
    parser.add_argument("--max_calls", type=int, default=1000, help="Maximum number of API calls.")
    parser.add_argument("--dry_run", type=int, default=None, help="Number of dry run rounds to execute without API calls.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    random.seed(args.seed)
    
    logging.info(f"Starting QWERTZ swap audit with arguments: {args}")

    if args.dry_run:
        logging.info(f"Performing a dry run of {args.dry_run} rounds.")
        for i in range(args.dry_run):
            text_length = random.randint(50, 300)
            text = ''.join(random.choices(string.ascii_letters + string.digits + ' ' + 'yzYZ', k=text_length))
            logging.info(f"Original text (sample): '{text[:80]}...'")
            best_substring = select_best_substring(text)
            if best_substring:
                swapped_text = qwertz_swap(best_substring)
                logging.info(f"  -> Best substring: '{best_substring}'")
                logging.info(f"  -> Swapped text:   '{swapped_text}'")
            else:
                logging.info("  -> No suitable substring found.")
        logging.info("Dry run complete.")
        return

    run_audit(args)


if __name__ == "__main__":
    main()
