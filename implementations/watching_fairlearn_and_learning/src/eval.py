import os
import json
from datetime import datetime

# Import the main functions from each module
from llm_replier import collect_replies
from fairlearn_processor import process_llm_data
from bias_evaluator import evaluate_fairlearn_bias

# Renamed the function from eval_script to eval
def eval(num_pairs=10000, log_file="error_log.txt"):
    """
    Runs the evaluation pipeline by calling Python functions directly.

    Args:
        num_pairs (int): Number of reply pairs to generate (default: 10000).
        log_file (str): The path to the log file for error logging.

    Returns:
        bool: True if all steps executed successfully, False otherwise.
    """
    personas = ["Mohamed", "John"]
    output_file = "llm_replies.parquet"
    
    all_success = True
    
    try:
        # Step 1: Generate LLM replies
        print("Step 1: Generating LLM replies...")
        for persona in personas:
            collect_replies(persona, num_pairs, output_file)
        print("LLM reply generation completed successfully.")
        
        # Step 2: Process the data
        print("Step 2: Processing data with Fairlearn...")
        processed_df = process_llm_data(output_file)
        print("Data processing completed successfully.")
        
        # Step 3: Evaluate bias
        print("Step 3: Evaluating bias...")
        results = evaluate_fairlearn_bias(processed_df)
        print("Bias evaluation completed successfully.")
        
        return True
        
    except Exception as e:
        print(f"Error during evaluation pipeline: {e}")
        with open(log_file, "a") as error_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_file.write(f"[{timestamp}] Error in evaluation pipeline: {e}\n")
        return False

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run bias evaluation pipeline")
    parser.add_argument("--num-pairs", type=int, default=10000, 
                        help="Number of reply pairs to generate (default: 10000)")
    args = parser.parse_args()
    
    log_file = os.path.join(os.path.dirname(__file__), "error_log.txt")
    
    print(f"Starting evaluation pipeline with {args.num_pairs} pairs...")
    success = eval(num_pairs=args.num_pairs, log_file=log_file)
    
    if success:
        print("\nEvaluation pipeline completed successfully. Review the outputs for insights.")
    else:
        print("\nEvaluation pipeline failed during execution. Check the error log for details.")
