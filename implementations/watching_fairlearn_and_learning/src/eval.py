"""
Module: eval

Orchestrates the full evaluation pipeline: LLM reply generation, data processing,
and bias evaluation.
"""

import os
import json
from datetime import datetime
import pandas as pd

# Import core pipeline functions
from llm_replier import collect_replies
from fairlearn_processor import process_llm_data
from bias_evaluator import evaluate_fairlearn_bias

def eval(num_pairs=10, log_file="error_log.txt"):
    """
    Runs the evaluation pipeline by calling Python functions directly.

    Args:
        num_pairs (int): Number of reply pairs to generate (default: 10).
        log_file (str): The path to the log file for error logging.

    Returns:
        bool: True if all steps executed successfully, False otherwise.
    """
    personas = ["Mohamed", "John"]
    output_file = "llm_replies.parquet"
    
    # Always use the correct available Groq model
    model_name = "llama3-8b-8192"
    run_id = None
    default_model = "llama3-8b-8192"

    # Only try to extract run_id from existing data if present
    if os.path.exists(output_file):
        try:
            df = pd.read_parquet(output_file)
            if not df.empty and "run_id" in df.columns and pd.notnull(df["run_id"].iloc[0]):
                run_id = df["run_id"].iloc[0]
        except Exception as e:
            print(f"Warning: Could not read {output_file} to extract run_id: {e}")
            model_name = default_model
    else:
        model_name = default_model

    if run_id is None:
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    all_success = True

    try:
        # Step 1: Generate LLM replies
        print(f"Step 1: Generating LLM replies with model: {model_name} and run_id: {run_id} ...")
        for persona in personas:
            try:
                collect_replies(persona, num_pairs, output_file, model_name, run_id, provider="groq")
            except Exception as e:
                print(f"[Groq ERROR] Failed to collect replies for persona '{persona}' with model '{model_name}': {e}")
                with open(log_file, "a") as error_file:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    error_file.write(f"[{timestamp}] [Groq ERROR] Persona: {persona}, Model: {model_name}, Error: {e}\n")
                all_success = False
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
    parser.add_argument("--num-pairs", type=int, default=10, 
                        help="Number of reply pairs to generate (default: 10)")
    args = parser.parse_args()
    
    log_file = os.path.join(os.path.dirname(__file__), "error_log.txt")
    
    print(f"Starting evaluation pipeline with {args.num_pairs} pairs...")
    success = eval(num_pairs=args.num_pairs, log_file=log_file)
    
    if success:
        print("\nEvaluation pipeline completed successfully. Review the outputs for insights.")
    else:
        print("\nEvaluation pipeline failed during execution. Check the error log for details.")
