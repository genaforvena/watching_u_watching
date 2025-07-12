"""
Main Module for Dual Bias Audit System

This module orchestrates the dual bias audit workflow, running both names bias and articles bias
studies in sequence, analyzing the results, and optionally publishing them to Hacker News.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from llm_client import LLMClient, create_llm_client, LLMResponse
from names_probe_generator import NamesProbeGenerator, NameProbePair
from articles_probe_generator import ArticlesProbeGenerator, ArticleProbePair
from bias_analyzer import (
    BiasAnalyzer, ResponseMetrics, StudyResults, analyze_study_results,
    generate_combined_report, generate_summary_for_self_evaluation
)
from publication import publish_results


class DualBiasAudit:
    """Main orchestration class for the dual bias audit system."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the dual bias audit system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = config.get("output_dir", "results")
        self.probe_count = config.get("probe_count", 50)
        self.skip_publication = config.get("skip_publication", False)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.llm_client = create_llm_client(
            endpoint_url=config["endpoint"],
            api_key=config["api_key"],
            client_type=config.get("client_type", "auto")
        )
        
        self.names_generator = NamesProbeGenerator(seed=42)
        self.articles_generator = ArticlesProbeGenerator(seed=42)
        self.bias_analyzer = BiasAnalyzer()
        
        # Initialize results storage
        self.names_study_results = None
        self.articles_study_results = None
        self.publication_result = None
        
        logging.info("Dual Bias Audit System initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = os.path.join(self.output_dir, "dual_bias_audit.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run(self) -> bool:
        """
        Run the dual bias audit workflow.
        
        Returns:
            bool: True if the audit completed successfully, False otherwise
        """
        try:
            logging.info("Starting dual bias audit")
            
            # Run names bias study
            logging.info("Running names bias study")
            self.names_study_results = self._run_names_bias_study()
            
            # Run articles bias study
            logging.info("Running articles bias study")
            self.articles_study_results = self._run_articles_bias_study()
            
            # Generate combined report
            logging.info("Generating combined report")
            combined_report = generate_combined_report(
                self.names_study_results,
                self.articles_study_results
            )
            
            # Save combined report
            report_path = os.path.join(self.output_dir, "combined_report.txt")
            with open(report_path, "w") as f:
                f.write(combined_report)
            logging.info(f"Combined report saved to {report_path}")
            
            # Publish results if not skipped
            if not self.skip_publication:
                logging.info("Publishing results")
                published, artistic_statement = publish_results(
                    self.llm_client,
                    self.names_study_results,
                    self.articles_study_results,
                    skip_publication=self.skip_publication,
                    hn_api_key=self.config.get("hn_api_key")
                )
                
                # Save artistic statement
                statement_path = os.path.join(self.output_dir, "artistic_statement.md")
                with open(statement_path, "w") as f:
                    f.write(artistic_statement)
                logging.info(f"Artistic statement saved to {statement_path}")
                
                self.publication_result = {
                    "published": published,
                    "artistic_statement": artistic_statement,
                    "timestamp": time.time()
                }
            
            # Log run to experiment_progress.json
            self._log_experiment_progress()
            
            logging.info("Dual bias audit completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error running dual bias audit: {e}", exc_info=True)
            return False
    
    def _run_names_bias_study(self) -> StudyResults:
        """
        Run the names bias study.
        
        Returns:
            StudyResults: Results of the names bias study
        """
        # Generate probe pairs
        probe_pairs = self.names_generator.generate_probe_pairs(self.probe_count)
        logging.info(f"Generated {len(probe_pairs)} name probe pairs")
        
        # Query LLM with probes
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            logging.info(f"Processing name probe pair {i+1}/{len(probe_pairs)}")
            
            # Query with Anglo name (baseline)
            baseline_result = self.llm_client.query(pair.anglo_prompt)
            baseline_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=baseline_result.response_text,
                response_time=baseline_result.response_time,
                probe_id=pair.pair_id + "_anglo",
                response_id=f"names_baseline_{i}"
            )
            baseline_responses.append(baseline_metrics)
            
            # Query with non-Anglo name (variant)
            variant_result = self.llm_client.query(pair.non_anglo_prompt)
            variant_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=variant_result.response_text,
                response_time=variant_result.response_time,
                probe_id=pair.pair_id + "_non_anglo",
                response_id=f"names_variant_{i}"
            )
            variant_responses.append(variant_metrics)
        
        # Analyze results
        study_results = analyze_study_results(
            baseline_responses=baseline_responses,
            variant_responses=variant_responses,
            study_type="names"
        )
        
        # Save results
        self._save_study_results(study_results, "names_study_results.json")
        
        # Generate and save report
        report = self.bias_analyzer.generate_bias_report(study_results.bias_analysis, "names")
        report_path = os.path.join(self.output_dir, "names_bias_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        logging.info(f"Names bias report saved to {report_path}")
        
        return study_results
    
    def _run_articles_bias_study(self) -> StudyResults:
        """
        Run the articles bias study.
        
        Returns:
            StudyResults: Results of the articles bias study
        """
        # Generate probe pairs
        probe_pairs = self.articles_generator.generate_probe_pairs(self.probe_count)
        logging.info(f"Generated {len(probe_pairs)} article probe pairs")
        
        # Query LLM with probes
        baseline_responses = []
        variant_responses = []
        
        for i, pair in enumerate(probe_pairs):
            logging.info(f"Processing article probe pair {i+1}/{len(probe_pairs)}")
            
            # Query with articles (baseline)
            baseline_result = self.llm_client.query(pair.with_articles_prompt)
            baseline_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=baseline_result.response_text,
                response_time=baseline_result.response_time,
                probe_id=pair.pair_id + "_with_articles",
                response_id=f"articles_baseline_{i}"
            )
            baseline_responses.append(baseline_metrics)
            
            # Query without articles (variant)
            variant_result = self.llm_client.query(pair.without_articles_prompt)
            variant_metrics = self.bias_analyzer.extract_response_metrics(
                response_text=variant_result.response_text,
                response_time=variant_result.response_time,
                probe_id=pair.pair_id + "_without_articles",
                response_id=f"articles_variant_{i}"
            )
            variant_responses.append(variant_metrics)
        
        # Analyze results
        study_results = analyze_study_results(
            baseline_responses=baseline_responses,
            variant_responses=variant_responses,
            study_type="articles"
        )
        
        # Save results
        self._save_study_results(study_results, "articles_study_results.json")
        
        # Generate and save report
        report = self.bias_analyzer.generate_bias_report(study_results.bias_analysis, "articles")
        report_path = os.path.join(self.output_dir, "articles_bias_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        logging.info(f"Articles bias report saved to {report_path}")
        
        return study_results
    
    def _save_study_results(self, study_results: StudyResults, filename: str):
        """
        Save study results to a file.
        
        Args:
            study_results: Study results to save
            filename: Name of the file to save to
        """
        # Convert to serializable format
        serializable_results = {
            "study_type": study_results.study_type,
            "timestamp": study_results.timestamp,
            "bias_analysis": {}
        }
        
        for metric_name, result in study_results.bias_analysis.items():
            serializable_results["bias_analysis"][metric_name] = {
                "metric_name": result.metric_name,
                "baseline_mean": result.baseline_mean,
                "variant_mean": result.variant_mean,
                "difference": result.difference,
                "ratio": result.ratio,
                "t_statistic": result.t_statistic,
                "p_value": result.p_value,
                "effect_size": result.effect_size,
                "bias_detected": result.bias_detected,
                "significance_level": result.significance_level,
                "sample_size_baseline": result.sample_size_baseline,
                "sample_size_variant": result.sample_size_variant
            }
        
        # Save to file
        results_path = os.path.join(self.output_dir, filename)
        with open(results_path, "w") as f:
            json.dump(serializable_results, f, indent=2)
        logging.info(f"Study results saved to {results_path}")
    
    def _log_experiment_progress(self):
        """Log the experiment progress to experiment_progress.json."""
        # Load existing progress if available
        progress_file = "experiment_progress.json"
        progress_data = {"results": []}
        
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r") as f:
                    progress_data = json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"Could not parse {progress_file}, creating new file")
        
        # Create entry for this run
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "names_study": {
                "bias_detected": self.names_study_results.has_bias if self.names_study_results else False,
                "metrics_analyzed": len(self.names_study_results.bias_analysis) if self.names_study_results else 0,
                "metrics_biased": sum(1 for r in self.names_study_results.bias_analysis.values() if r.bias_detected) if self.names_study_results else 0
            },
            "articles_study": {
                "bias_detected": self.articles_study_results.has_bias if self.articles_study_results else False,
                "metrics_analyzed": len(self.articles_study_results.bias_analysis) if self.articles_study_results else 0,
                "metrics_biased": sum(1 for r in self.articles_study_results.bias_analysis.values() if r.bias_detected) if self.articles_study_results else 0
            },
            "published": self.publication_result.get("published", False) if self.publication_result else False,
            "config": {
                "probe_count": self.probe_count,
                "skip_publication": self.skip_publication,
                "endpoint": self.config.get("endpoint", "").split("/")[-1]  # Just the last part for privacy
            }
        }
        
        # Add to results
        progress_data["results"].append(entry)
        
        # Save progress
        with open(progress_file, "w") as f:
            json.dump(progress_data, f, indent=2)
        logging.info(f"Experiment progress logged to {progress_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dual Bias Audit System")
    
    parser.add_argument("--endpoint", required=True, help="URL of the LLM endpoint")
    parser.add_argument("--api-key", required=True, help="API key for the LLM endpoint")
    parser.add_argument("--probe-count", type=int, default=50, help="Number of probe pairs per study (default: 50)")
    parser.add_argument("--skip-publication", action="store_true", help="Skip publication to Hacker News")
    parser.add_argument("--output-dir", default="results", help="Directory to save results (default: results)")
    parser.add_argument("--client-type", choices=["auto", "openai", "anthropic"], default="auto",
                       help="Type of LLM client to use (default: auto)")
    parser.add_argument("--hn-api-key", help="API key for Hacker News (optional)")
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        "endpoint": args.endpoint,
        "api_key": args.api_key,
        "probe_count": args.probe_count,
        "skip_publication": args.skip_publication,
        "output_dir": args.output_dir,
        "client_type": args.client_type,
        "hn_api_key": args.hn_api_key
    }
    
    # Run audit
    audit = DualBiasAudit(config)
    success = audit.run()
    
    if success:
        print("Dual bias audit completed successfully. See results in the output directory.")
        sys.exit(0)
    else:
        print("Dual bias audit failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()