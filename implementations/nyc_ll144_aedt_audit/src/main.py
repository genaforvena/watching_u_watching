#!/usr/bin/env python3
"""
Main orchestration module for NYC Local Law 144 AEDT Audit.

This module serves as the entry point for conducting audits of Automated Employment
Decision Tools (AEDTs) in compliance with NYC Local Law 144.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from .aedt_probe_generator import AEDTProbeGenerator
from .submission_system import SubmissionSystem
from .response_collector import ResponseCollector
from .ll144_metrics import LL144MetricsCalculator
from .data_storage import DataStorage
from .analyze_responses import ResponseAnalyzer


def setup_logging(config):
    """Set up logging based on configuration."""
    log_level = getattr(logging, config["logging"]["level"])
    log_format = config["logging"]["format"]
    log_file = config["logging"]["file"]
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def run_audit(config, logger, mode="once", dry_run=False):
    """Run the AEDT audit process."""
    logger.info(f"Starting AEDT audit in {mode} mode (dry_run={dry_run})")
    
    # Initialize components
    data_storage = DataStorage(
        db_path=config["storage"]["database_path"],
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
    num_pairs = config["probe_generation"]["num_pairs"]
    logger.info(f"Generating {num_pairs} probe pairs")
    probes = probe_generator.generate_probes(num_pairs)
    
    # Submit probes
    logger.info(f"Submitting {len(probes)} probes to AEDT")
    submission_results = []
    for probe in probes:
        result = submission_system.submit_probe(probe)
        submission_results.append(result)
        data_storage.store_submission(probe, result)
    
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
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Audit completed. Report saved to {report_path}")
    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="NYC Local Law 144 AEDT Audit Tool")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--mode", choices=["once", "scheduled"], default="once", help="Audit mode")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual submissions)")
    args = parser.parse_args()
    
    config = load_config(args.config)
    logger = setup_logging(config)
    
    try:
        run_audit(config, logger, mode=args.mode, dry_run=args.dry_run)
    except Exception as e:
        logger.exception(f"Error during audit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()