"""
Main Orchestration Script for Berlin Housing Bias Testing

This script coordinates all components of the automated paired testing system
for detecting bias in the Berlin housing market on Immobilienscout24.de.
"""

import json
import logging
import schedule
import time
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from property_monitor import create_monitor_from_config
from application_generator import create_generator_from_config  
from submission_system import create_submission_system_from_config
from pii_redactor import create_redactor_from_config
from data_storage import create_storage_from_config


class BerlinHousingBiasTest:
    """
    Main orchestration class for the housing bias testing system.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the bias testing system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
        
        # Initialize components
        self.pii_redactor = create_redactor_from_config(self.config)
        self.data_storage = create_storage_from_config(self.config, self.pii_redactor)
        self.property_monitor = create_monitor_from_config(self.config)
        self.application_generator = create_generator_from_config(self.config)
        self.submission_system = create_submission_system_from_config(self.config)
        
        # Setup logging
        self._setup_logging()
        
        # Track system state
        self.last_monitoring_check = None
        self.total_properties_found = 0
        self.total_applications_sent = 0
        self.system_start_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logging.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logging.error(f"Configuration file {self.config_path} not found")
            logging.info("Please copy config.example.json to config.json and adjust settings")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_file = log_config.get('file', 'logs/berlin_housing_test.log')
        
        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Limit log file size
        if log_config.get('max_file_size_mb'):
            import logging.handlers
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=log_config['max_file_size_mb'] * 1024 * 1024,
                backupCount=log_config.get('backup_count', 5)
            )
            logging.getLogger().addHandler(file_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logging.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    def monitoring_cycle(self):
        """Execute one monitoring cycle to check for new properties."""
        try:
            logging.info("Starting monitoring cycle...")
            self.last_monitoring_check = datetime.now()
            
            # Check for new properties
            new_properties = self.property_monitor.check_for_new_properties()
            
            if not new_properties:
                logging.info("No new properties found")
                return
            
            self.total_properties_found += len(new_properties)
            logging.info(f"Found {len(new_properties)} new properties")
            
            # Process each new property
            for property_data in new_properties:
                try:
                    self._process_new_property(property_data)
                except Exception as e:
                    logging.error(f"Error processing property {property_data.get('id')}: {e}")
                    continue
            
            logging.info("Monitoring cycle completed successfully")
            
        except Exception as e:
            logging.error(f"Error in monitoring cycle: {e}")
    
    def _process_new_property(self, property_data: Dict):
        """Process a newly discovered property."""
        property_id = property_data.get('id')
        logging.info(f"Processing new property: {property_id}")
        
        # Store property data
        if not self.data_storage.store_property(property_data):
            logging.error(f"Failed to store property {property_id}")
            return
        
        # Generate paired applications
        applications = self.application_generator.generate_paired_applications(property_data)
        
        if len(applications) != 2:
            logging.error(f"Expected 2 applications for property {property_id}, got {len(applications)}")
            return
        
        # Store applications
        for application in applications:
            if not self.data_storage.store_application(application):
                logging.error(f"Failed to store application for {application['persona']}")
                continue
        
        # Submit applications
        submission_results = self.submission_system.submit_paired_applications(
            applications,
            dry_run=self.config.get('dry_run', True),
            redirect_all_emails_to=self.config.get('redirect_all_emails_to')
        )
        
        # Store submission results
        for result in submission_results:
            if not self.data_storage.store_submission(result):
                logging.error(f"Failed to store submission result")
                continue
            
            if result['success']:
                self.total_applications_sent += 1
        
        successful_submissions = len([r for r in submission_results if r['success']])
        logging.info(f"Property {property_id}: {successful_submissions}/{len(submission_results)} applications submitted successfully")
    
    def maintenance_cycle(self):
        """Execute maintenance tasks."""
        try:
            logging.info("Starting maintenance cycle...")
            
            # Backup data
            if self.data_storage.backup_data():
                logging.info("Data backup completed")
            
            # Clean up old data
            self.data_storage.cleanup_old_data()
            
            # Print statistics
            stats = self._get_system_statistics()
            logging.info(f"System statistics: {stats}")
            
            logging.info("Maintenance cycle completed")
            
        except Exception as e:
            logging.error(f"Error in maintenance cycle: {e}")
    
    def _get_system_statistics(self) -> Dict:
        """Get comprehensive system statistics."""
        stats = self.data_storage.get_statistics()
        
        # Add runtime statistics
        if self.system_start_time:
            runtime = datetime.now() - self.system_start_time
            stats['runtime_hours'] = runtime.total_seconds() / 3600
        
        stats['total_properties_found'] = self.total_properties_found
        stats['total_applications_sent'] = self.total_applications_sent
        stats['last_monitoring_check'] = self.last_monitoring_check.isoformat() if self.last_monitoring_check else None
        
        # Add submission system statistics
        submission_stats = self.submission_system.get_submission_stats()
        stats.update(submission_stats)
        
        return stats
    
    def run_once(self):
        """Run one complete cycle (for testing/manual execution)."""
        logging.info("Running single execution cycle...")
        self.monitoring_cycle()
        
    def run_scheduled(self):
        """Run the system with scheduled monitoring."""
        self.system_start_time = datetime.now()
        self.running = True
        
        monitoring_config = self.config.get('monitoring', {})
        poll_interval = monitoring_config.get('poll_interval_minutes', 30)
        
        logging.info(f"Starting scheduled monitoring (checking every {poll_interval} minutes)")
        
        # Schedule monitoring cycles
        schedule.every(poll_interval).minutes.do(self.monitoring_cycle)
        
        # Schedule maintenance (daily at 3 AM)
        schedule.every().day.at("03:00").do(self.maintenance_cycle)
        
        # Initial monitoring cycle
        self.monitoring_cycle()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logging.info("Keyboard interrupt received")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
        
        self._shutdown()
    
    def analyze_responses(self):
        """Analyze collected responses for bias patterns."""
        logging.info("Starting response analysis...")
        
        try:
            analysis_data = self.data_storage.get_bias_analysis_data()
            
            if analysis_data.empty:
                logging.info("No data available for analysis yet")
                return
            
            # Basic bias indicators
            total_properties = len(analysis_data)
            properties_with_responses = len(analysis_data[analysis_data['total_responses'] > 0])
            
            mohammed_responses = analysis_data['mohammed_responses'].sum()
            franz_responses = analysis_data['franz_responses'].sum()
            
            logging.info(f"Analysis Results:")
            logging.info(f"  Total properties tested: {total_properties}")
            logging.info(f"  Properties with responses: {properties_with_responses}")
            logging.info(f"  Mohammed responses: {mohammed_responses}")
            logging.info(f"  Franz responses: {franz_responses}")
            
            if mohammed_responses + franz_responses > 0:
                mohammed_rate = mohammed_responses / (mohammed_responses + franz_responses)
                franz_rate = franz_responses / (mohammed_responses + franz_responses)
                
                logging.info(f"  Mohammed response rate: {mohammed_rate:.2%}")
                logging.info(f"  Franz response rate: {franz_rate:.2%}")
                
                # Simple bias indicator
                if franz_responses > 0:
                    bias_ratio = mohammed_responses / franz_responses
                    logging.info(f"  Response ratio (Mohammed/Franz): {bias_ratio:.2f}")
                    
                    if bias_ratio < 0.8:
                        logging.warning("  POTENTIAL BIAS DETECTED: Mohammed receiving significantly fewer responses")
                    elif bias_ratio > 1.2:
                        logging.warning("  ANOMALY DETECTED: Mohammed receiving more responses (unusual pattern)")
                    else:
                        logging.info("  No significant bias detected in response rates")
            
        except Exception as e:
            logging.error(f"Error in response analysis: {e}")
    
    def _shutdown(self):
        """Graceful shutdown of all components."""
        logging.info("Shutting down system...")
        
        try:
            # Close browser connections
            self.property_monitor.cleanup()
            self.submission_system.cleanup()
            
            # Final statistics
            final_stats = self._get_system_statistics()
            logging.info(f"Final system statistics: {final_stats}")
            
            logging.info("System shutdown completed")
            
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Berlin Housing Bias Testing System")
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--mode', choices=['once', 'scheduled', 'analyze'], default='once',
                       help='Execution mode: once (single run), scheduled (continuous), analyze (analyze results)')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually submitting applications')
    parser.add_argument('--redirect-all-emails-to', type=str, default=None,
                        help='If set, redirects all outgoing application emails to this address (for dry-run/testing)')

    args = parser.parse_args()

    try:
        # Initialize system
        bias_test = BerlinHousingBiasTest(args.config)

        # Override dry-run setting if specified
        if args.dry_run:
            bias_test.config['dry_run'] = True
            logging.info("DRY RUN MODE: Applications will not be actually submitted")

        # Set email redirection if specified
        if args.redirect_all_emails_to:
            bias_test.config['redirect_all_emails_to'] = args.redirect_all_emails_to
            logging.info(f"All outgoing application emails will be redirected to: {args.redirect_all_emails_to}")

        # Execute based on mode
        if args.mode == 'once':
            bias_test.run_once()
        elif args.mode == 'scheduled':
            bias_test.run_scheduled()
        elif args.mode == 'analyze':
            bias_test.analyze_responses()

    except KeyboardInterrupt:
        logging.info("Execution interrupted by user")
    except Exception as e:
        logging.error(f"System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()