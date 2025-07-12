"""
Main Audit Class for British Airways Customer Service Responsiveness Bias Audit

This module implements the main audit class that integrates probe generation
and response analysis components for detecting bias in customer service responsiveness.
"""

import time
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# Assuming these are provided by the framework
from core.audit import CorrespondenceAudit
from core.ethics import ethical_review_hook
from core.decorators import rate_limiter

from .constants import (
    VARIATIONS,
    MIN_PROBES,
    COMPATIBILITY_VERSION,
    AUDIT_METADATA,
    MAX_REQUESTS_PER_DAY
)
from .probe_generation import (
    generate_probe_batch,
    validate_probe_content,
    Probe,
    ethical_review_variations
)
from .response_analysis import (
    Response,
    process_response,
    detect_bias,
    calculate_minimum_sample_size
)
from .simulation import ResponseSimulator, create_simulator_with_bias


class BACustomerServiceAudit(CorrespondenceAudit):
    """
    Audit class for detecting bias in British Airways customer service responsiveness.
    """
    
    # Class constants
    VARIATIONS = VARIATIONS
    MIN_PROBES = MIN_PROBES
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the audit.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        super().__init__(config)
        
        # Initialize configuration
        self.config = config or {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.probes = []
        self.responses = []
        self.results = None
        self.start_time = None
        self.end_time = None
        
        # Verify compatibility
        if not self._check_compatibility():
            raise RuntimeError(f"Incompatible framework version. Requires >= {COMPATIBILITY_VERSION}")
        
        self.logger.info("British Airways Customer Service Responsiveness Bias Audit initialized")
    
    def _check_compatibility(self) -> bool:
        """
        Check if the current framework version is compatible.
        
        Returns:
            True if compatible, False otherwise
        """
        # This would normally check against the actual framework version
        # For now, we'll assume it's compatible
        return COMPATIBILITY_VERSION >= 1.2
    
    @rate_limiter(requests=MAX_REQUESTS_PER_DAY, period=86400)  # 86400 seconds = 24 hours
    def generate_probes(self, num_pairs: int) -> List[Probe]:
        """
        Generate probe pairs for the audit.
        
        Args:
            num_pairs: Number of probe pairs to generate
            
        Returns:
            List of generated probes
        """
        self.logger.info(f"Generating {num_pairs} probe pairs")
        
        # Perform ethical review of variations
        ethical_review_hook(self.VARIATIONS)
        ethical_review_variations(self.VARIATIONS)
        
        # Calculate batch size based on rate limits
        batch_size = min(10, num_pairs)
        
        all_probes = []
        remaining_pairs = num_pairs
        
        while remaining_pairs > 0:
            current_batch_size = min(batch_size, remaining_pairs)
            self.logger.info(f"Generating batch of {current_batch_size} probe pairs")
            
            # Generate a batch of probe pairs
            probe_pairs = generate_probe_batch(current_batch_size)
            
            # Flatten the pairs into a list of probes
            batch_probes = [probe for pair in probe_pairs for probe in pair]
            
            # Validate probes
            valid_probes = [p for p in batch_probes if validate_probe_content(p)]
            
            # Add valid probes to the list
            all_probes.extend(valid_probes)
            
            # Update remaining pairs
            valid_pairs = len(valid_probes) // 2
            remaining_pairs -= valid_pairs
            
            self.logger.info(f"Generated {valid_pairs} valid probe pairs in this batch")
            
            # Sleep to respect rate limits
            if remaining_pairs > 0:
                time.sleep(60)  # Sleep for 1 minute between batches
        
        self.probes = all_probes
        self.logger.info(f"Generated a total of {len(all_probes)} probes ({len(all_probes) // 2} pairs)")
        
        return all_probes
    
    def submit_probes(self, probes: Optional[List[Probe]] = None) -> None:
        """
        Submit probes to the customer service system.
        
        Args:
            probes: Optional list of probes to submit (uses self.probes if None)
        """
        probes = probes or self.probes
        self.logger.info(f"Submitting {len(probes)} probes")
        
        # In a real implementation, this would actually submit the probes
        # For this simulation, we'll just log that they were submitted
        for probe in probes:
            self.logger.info(f"Submitted probe {probe.probe_id} (variation: {probe.variation})")
            
            # Add a small delay between submissions to avoid rate limiting
            time.sleep(1)
    
    def collect_responses(self, max_wait_time: int = 14 * 24 * 60 * 60) -> List[Response]:
        """
        Collect responses to the submitted probes.
        
        Args:
            max_wait_time: Maximum time to wait for responses (in seconds)
            
        Returns:
            List of Response objects
        """
        self.logger.info(f"Collecting responses (max wait time: {max_wait_time} seconds)")
        
        # Check if we're in test mode
        if self.config.get("test_mode", False):
            # Use the simulator for testing
            bias_level = self.config.get("bias_level", "medium")
            simulator = create_simulator_with_bias(bias_level)
            responses = simulator.simulate_responses_batch(self.probes)
            self.logger.info(f"Simulated {len(responses)} responses with bias level: {bias_level}")
        else:
            # In a real implementation, this would actually collect responses
            # For this simulation, we'll create simulated responses
            simulator = ResponseSimulator()
            responses = simulator.simulate_responses_batch(self.probes)
            self.logger.info(f"Simulated {len(responses)} responses")
        
        self.responses = responses
        return responses
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the results of the audit.
        
        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Analyzing results")
        
        if not self.responses:
            self.logger.warning("No responses to analyze")
            return {"error": "No responses to analyze"}
        
        # Detect bias in the responses
        results = detect_bias(self.responses)
        
        # Add metadata to results
        results["metadata"] = {
            "audit_id": f"ba_cs_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "probe_count": len(self.probes),
            "response_count": len(self.responses),
            "audit_duration_hours": (self.end_time - self.start_time) / 3600 if self.start_time and self.end_time else None
        }
        
        self.results = results
        
        # Log summary of results
        bias_detected = results.get("bias_detected", False)
        self.logger.info(f"Analysis complete. Bias detected: {bias_detected}")
        
        return results
    
    def run_audit(self, num_pairs: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the complete audit process.
        
        Args:
            num_pairs: Number of probe pairs to generate (defaults to MIN_PROBES)
            
        Returns:
            Dictionary with audit results
        """
        num_pairs = num_pairs or self.MIN_PROBES
        self.logger.info(f"Starting audit with {num_pairs} probe pairs")
        
        self.start_time = time.time()
        
        try:
            # Generate probes
            probes = self.generate_probes(num_pairs)
            
            # Submit probes
            self.submit_probes(probes)
            
            # Collect responses
            self.collect_responses()
            
            # Analyze results
            results = self.analyze_results()
            
            self.end_time = time.time()
            self.logger.info("Audit completed successfully")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running audit: {e}")
            return {"error": str(e)}
    
    def get_power_analysis(self) -> Dict[str, Any]:
        """
        Get power analysis for the audit.
        
        Returns:
            Dictionary with power analysis results
        """
        # Calculate minimum sample size
        min_sample_size = calculate_minimum_sample_size()
        
        return {
            "effect_size": 0.15,  # 15% difference in response rate
            "power": 0.8,
            "alpha": 0.05,
            "min_sample_size_per_group": min_sample_size,
            "total_probes_needed": min_sample_size * 2
        }
    
    def export_results(self, format: str = "json") -> str:
        """
        Export audit results to the specified format.
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            String with exported results
        """
        if not self.results:
            return "No results to export"
        
        if format.lower() == "json":
            return json.dumps(self.results, indent=2)
        elif format.lower() == "csv":
            # In a real implementation, this would convert results to CSV
            return "CSV export not implemented"
        else:
            return f"Unsupported export format: {format}"