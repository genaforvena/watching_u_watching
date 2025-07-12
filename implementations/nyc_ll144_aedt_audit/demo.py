#!/usr/bin/env python3
"""
Demonstration of NYC Local Law 144 AEDT Audit Implementation.

This script demonstrates the functionality of the NYC Local Law 144 AEDT Audit Implementation
by running a simplified audit process in dry-run mode.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from src.aedt_probe_generator import AEDTProbeGenerator
from src.submission_system import SubmissionSystem
from src.response_collector import ResponseCollector
from src.ll144_metrics import LL144MetricsCalculator
from src.analyze_responses import ResponseAnalyzer
from src.data_storage import DataStorage
from src.pii_redactor import PIIRedactor


def setup_logging():
    """Set up logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config():
    """Load configuration."""
    config_path = "config.json"
    
    # Use example config if config.json doesn't exist
    if not os.path.exists(config_path):
        config_path = "config.example.json"
    
    with open(config_path, 'r') as f:
        return json.load(f)


def run_demo(logger, config, num_pairs=10, dry_run=True):
    """Run the demonstration.
    
    Args:
        logger: Logger instance
        config: Configuration dictionary
        num_pairs: Number of probe pairs to generate
        dry_run: Whether to run in dry-run mode
    """
    logger.info(f"Starting NYC Local Law 144 AEDT Audit Demo (dry_run={dry_run})")
    
    # Create output directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("visualizations", exist_ok=True)
    
    # Initialize components
    logger.info("Initializing components")
    
    data_storage = DataStorage(
        db_path="data/aedt_audit_demo.db",
        backup_enabled=config["storage"]["backup_enabled"],
        backup_interval=config["storage"]["backup_interval_hours"],
        retention_days=config["storage"]["data_retention_days"]
    )
    
    probe_generator = AEDTProbeGenerator(
        job_types=config["probe_generation"]["job_types"],
        protected_characteristics=config["probe_generation"]["protected_characteristics"],
        control_variables=config["probe_generation"]["control_variables"]
    )
    
    submission_system = SubmissionSystem(
        aedt_config=config["aedt"],
        rate_limit=config["submission"]["rate_limit"],
        timeout=config["submission"]["timeout"],
        retry_config=config["submission"]["retry"],
        dry_run=dry_run
    )
    
    response_collector = ResponseCollector(
        methods=config["response_collection"]["methods"],
        email_config=config["response_collection"]["email_config"] if "email" in config["response_collection"]["methods"] else None,
        check_interval=config["response_collection"]["check_interval_minutes"],
        max_wait_days=config["response_collection"]["max_wait_days"],
        dry_run=dry_run
    )
    
    metrics_calculator = LL144MetricsCalculator(
        metrics=config["analysis"]["metrics"],
        thresholds=config["analysis"]["thresholds"]
    )
    
    analyzer = ResponseAnalyzer(
        metrics_calculator=metrics_calculator,
        output_format=config["analysis"]["output_format"]
    )
    
    # Generate probes
    logger.info(f"Generating {num_pairs} probe pairs")
    probes = probe_generator.generate_probes(num_pairs)
    
    # Display probe examples
    logger.info("Probe examples:")
    for i, probe in enumerate(probes[:2]):
        logger.info(f"Probe {i+1}:")
        logger.info(f"  ID: {probe.id}")
        logger.info(f"  Job Type: {probe.job_type}")
        logger.info(f"  Variation: {probe.variation}")
        logger.info(f"  Pair ID: {probe.pair_id}")
    
    # Submit probes
    logger.info(f"Submitting {len(probes)} probes")
    submission_results = []
    for probe in probes:
        result = submission_system.submit_probe(probe.to_dict())
        submission_results.append(result)
        data_storage.store_submission(probe.to_dict(), result)
    
    # Collect responses
    logger.info("Collecting responses")
    responses = response_collector.collect_responses(submission_results)
    for response in responses:
        data_storage.store_response(response)
    
    # Analyze results
    logger.info("Analyzing results")
    analysis_results = analyzer.analyze_responses(responses)
    data_storage.store_analysis_results(analysis_results)
    
    # Generate report
    logger.info("Generating report")
    report = analyzer.generate_report(analysis_results)
    report_path = f"reports/aedt_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate visualizations
    logger.info("Generating visualizations")
    visualization_paths = analyzer.generate_visualizations(analysis_results, "visualizations")
    
    # Display results summary
    logger.info("\nResults Summary:")
    logger.info(f"Generated {len(probes)} probes ({num_pairs} pairs)")
    logger.info(f"Collected {len(responses)} responses")
    
    # Display selection rates
    selection_rates = {}
    for group, data in analysis_results["metrics"]["selection_rates"].items():
        selection_rates[group] = f"{data['selected']}/{data['total']} = {data['rate']:.2f}"
    
    logger.info("\nSelection Rates:")
    for group, rate in selection_rates.items():
        logger.info(f"  {group}: {rate}")
    
    # Display disparate impact
    if "disparate_impact" in analysis_results["metrics"]:
        logger.info("\nDisparate Impact:")
        for pair, impact in analysis_results["metrics"]["disparate_impact"].items():
            logger.info(f"  {pair}: {impact['ratio']:.2f} (Adverse Impact: {impact['adverse_impact']})")
    
    logger.info(f"\nReport saved to: {report_path}")
    logger.info(f"Visualizations saved to: {', '.join(visualization_paths)}")
    
    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="NYC Local Law 144 AEDT Audit Demo")
    parser.add_argument("--num-pairs", type=int, default=10, help="Number of probe pairs to generate")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual submissions)")
    args = parser.parse_args()
    
    logger = setup_logging()
    config = load_config()
    
    try:
        run_demo(logger, config, num_pairs=args.num_pairs, dry_run=args.dry_run)
    except Exception as e:
        logger.exception(f"Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()