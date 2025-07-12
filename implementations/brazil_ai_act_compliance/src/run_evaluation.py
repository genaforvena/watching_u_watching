"""
run_evaluation.py

This module provides a single entry point for running the full evaluation pipeline
for Brazil's AI Act compliance.
"""

import os
import json
import logging
import argparse
import time
from typing import Dict, Any

from employment_bias_evaluator import EmploymentBiasEvaluator
from brazil_aia_generator import BrazilAIAGenerator
from explanation_generator import ExplanationGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("brazil_ai_act_compliance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_full_evaluation(config_path: str = "config.json", output_dir: str = "output", num_pairs: int = 100) -> Dict[str, Any]:
    """
    Run the full evaluation pipeline for Brazil's AI Act compliance.

    Args:
        config_path: Path to the configuration file
        output_dir: Output directory for results
        num_pairs: Number of application pairs to generate

    Returns:
        Dict[str, Any]: Dictionary with evaluation results
    """
    start_time = time.time()
    logger.info(f"Starting full evaluation pipeline with {num_pairs} pairs")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Run employment bias evaluation
    logger.info("Step 1: Running employment bias evaluation")
    bias_evaluator = EmploymentBiasEvaluator(config_path)
    bias_evaluator.output_dir = output_dir
    bias_results = bias_evaluator.run_evaluation(num_pairs)
    
    # Step 2: Generate AIA report
    logger.info("Step 2: Generating AIA report")
    bias_analysis_path = os.path.join(output_dir, f"bias_analysis_{bias_evaluator.run_id}.json")
    aia_generator = BrazilAIAGenerator(config_path, bias_analysis_path)
    aia_generator.output_dir = output_dir
    aia_results = aia_generator.generate_aia("both")
    
    # Step 3: Generate explanations for a sample of decisions
    logger.info("Step 3: Generating explanations for sample decisions")
    explanation_generator = ExplanationGenerator(config_path)
    explanation_generator.output_dir = output_dir
    
    # Generate explanations for a sample of decisions (5 selected, 5 rejected)
    responses_df = bias_results["responses_df"]
    selected_samples = responses_df[responses_df["selected"]].head(5).to_dict("records")
    rejected_samples = responses_df[~responses_df["selected"]].head(5).to_dict("records")
    
    explanation_results = {
        "selected": [],
        "rejected": []
    }
    
    # Generate explanations for selected samples
    for sample in selected_samples:
        explanation = explanation_generator.generate_explanation_for_decision(sample, "all", "en")
        explanation_results["selected"].append({
            "decision_id": sample.get("application_id", ""),
            "explanation_paths": {
                "json": os.path.join(output_dir, f"explanations_{sample.get('application_id', '')}.json"),
                "markdown": os.path.join(output_dir, f"explanation_{sample.get('application_id', '')}_en.md")
            }
        })
    
    # Generate explanations for rejected samples
    for sample in rejected_samples:
        explanation = explanation_generator.generate_explanation_for_decision(sample, "all", "en")
        explanation_results["rejected"].append({
            "decision_id": sample.get("application_id", ""),
            "explanation_paths": {
                "json": os.path.join(output_dir, f"explanations_{sample.get('application_id', '')}.json"),
                "markdown": os.path.join(output_dir, f"explanation_{sample.get('application_id', '')}_en.md")
            }
        })
    
    # Generate Portuguese explanations for one selected and one rejected sample
    if selected_samples:
        pt_explanation = explanation_generator.generate_explanation_for_decision(selected_samples[0], "human_readable", "pt")
        explanation_results["selected"][0]["explanation_paths"]["markdown_pt"] = os.path.join(output_dir, f"explanation_{selected_samples[0].get('application_id', '')}_pt.md")
    
    if rejected_samples:
        pt_explanation = explanation_generator.generate_explanation_for_decision(rejected_samples[0], "human_readable", "pt")
        explanation_results["rejected"][0]["explanation_paths"]["markdown_pt"] = os.path.join(output_dir, f"explanation_{rejected_samples[0].get('application_id', '')}_pt.md")
    
    # Compile results
    results = {
        "bias_evaluation": {
            "run_id": bias_evaluator.run_id,
            "num_pairs": num_pairs,
            "report_path": os.path.join(output_dir, f"bias_report_{bias_evaluator.run_id}.md"),
            "analysis_path": bias_analysis_path
        },
        "aia": {
            "report_id": aia_results["aia_report"]["metadata"]["report_id"],
            "json_path": aia_results["json_path"],
            "markdown_path": aia_results["markdown_path"]
        },
        "explanations": explanation_results,
        "runtime_seconds": time.time() - start_time
    }
    
    # Save results summary
    results_path = os.path.join(output_dir, "evaluation_results_summary.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved evaluation results summary to {results_path}")
    
    logger.info(f"Full evaluation pipeline completed in {results['runtime_seconds']:.2f} seconds")
    
    return results


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Run the full evaluation pipeline for Brazil's AI Act compliance")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--num-pairs", type=int, default=100, help="Number of application pairs to generate")
    args = parser.parse_args()
    
    # Run full evaluation
    results = run_full_evaluation(args.config, args.output_dir, args.num_pairs)
    
    print("\nEvaluation pipeline completed successfully!")
    print(f"Bias evaluation report: {results['bias_evaluation']['report_path']}")
    print(f"AIA report: {results['aia']['markdown_path']}")
    print(f"Explanations generated: {len(results['explanations']['selected']) + len(results['explanations']['rejected'])}")
    print(f"Results summary: {os.path.join(args.output_dir, 'evaluation_results_summary.json')}")
    print(f"Total runtime: {results['runtime_seconds']:.2f} seconds")


if __name__ == "__main__":
    main()