"""
Probe Generation Module for British Airways Customer Service Responsiveness Bias Audit

This module handles the generation of synthetic customer service inquiries
for testing potential bias in response patterns based on perceived identity.
"""

import uuid
import random
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from functools import wraps

from .constants import (
    INQUIRY_TEMPLATES,
    IDENTITY_GROUPS,
    EMAIL_TEMPLATE,
    PLACEHOLDER_VALUES,
    InquiryType,
    MAX_INQUIRIES_PER_DAY,
    RATE_LIMIT_PERIOD
)


class ProbeGenerationError(Exception):
    """Exception raised for errors in probe generation."""
    pass


def rate_limiter(requests: int, period: int):
    """
    Decorator to limit the rate of function calls.
    
    Args:
        requests: Maximum number of requests allowed in the period
        period: Time period in seconds
    """
    def decorator(func):
        # Store the timestamps of function calls
        timestamps = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Remove timestamps older than the period
            while timestamps and current_time - timestamps[0] > period:
                timestamps.pop(0)
            
            # Check if we've exceeded the rate limit
            if len(timestamps) >= requests:
                wait_time = period - (current_time - timestamps[0])
                if wait_time > 0:
                    time.sleep(wait_time)
                    # Update current time after waiting
                    current_time = time.time()
                    # Remove timestamps older than the period again
                    while timestamps and current_time - timestamps[0] > period:
                        timestamps.pop(0)
            
            # Add current timestamp
            timestamps.append(current_time)
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def ethical_review_hook(variations: Dict) -> bool:
    """
    Validate that probe variations meet ethical standards.
    
    Args:
        variations: Dictionary of probe variations to validate
        
    Returns:
        bool: True if variations pass ethical review, False otherwise
        
    Raises:
        ValueError: If variations contain potential ethical issues
    """
    # Check for real PII
    for group, data in variations.items():
        for email in data.get("emails", []):
            if not email.endswith("@example.com"):
                raise ValueError(f"Potential real email detected: {email}")
    
    # Check for appropriate inquiry content
    for group, data in variations.items():
        for name in data.get("names", []):
            if len(name.split()) < 2:
                raise ValueError(f"Invalid name format: {name}")
    
    # All checks passed
    return True


class ProbeGenerator:
    """
    Generates synthetic customer service inquiries for bias testing.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the probe generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Validate identity groups
        for group, data in IDENTITY_GROUPS.items():
            if len(data.get("names", [])) != len(data.get("emails", [])):
                raise ValueError(f"Names and emails must have the same length for group {group}")
    
    def _generate_inquiry_details(self, inquiry_type: InquiryType) -> Tuple[str, str]:
        """
        Generate inquiry details for a specific type.
        
        Args:
            inquiry_type: Type of inquiry to generate
            
        Returns:
            Tuple containing subject and details
        """
        template = INQUIRY_TEMPLATES.get(inquiry_type)
        if not template:
            raise ProbeGenerationError(f"No template found for inquiry type: {inquiry_type}")
        
        subject = template["subject"]
        details = template["details"]
        
        # Replace placeholders with random values
        for placeholder, values in PLACEHOLDER_VALUES.items():
            if placeholder in details:
                details = details.replace(f"[{placeholder}]", random.choice(values))
        
        return subject, details
    
    def _select_identity(self, group: str) -> Tuple[str, str]:
        """
        Select a random identity from the specified group.
        
        Args:
            group: Identity group to select from
            
        Returns:
            Tuple containing name and email
        """
        if group not in IDENTITY_GROUPS:
            raise ProbeGenerationError(f"Unknown identity group: {group}")
        
        group_data = IDENTITY_GROUPS[group]
        index = random.randrange(len(group_data["names"]))
        
        return group_data["names"][index], group_data["emails"][index]
    
    @rate_limiter(requests=MAX_INQUIRIES_PER_DAY, period=RATE_LIMIT_PERIOD)
    def generate_probe(self, group: str, inquiry_type: Optional[InquiryType] = None) -> Dict:
        """
        Generate a single probe for the specified group.
        
        Args:
            group: Identity group to use
            inquiry_type: Type of inquiry to generate (random if None)
            
        Returns:
            Dictionary containing probe data
        """
        # Select random inquiry type if not specified
        if inquiry_type is None:
            inquiry_type = random.choice(list(InquiryType))
        
        # Generate inquiry details
        subject, details = self._generate_inquiry_details(inquiry_type)
        
        # Select identity
        name, email = self._select_identity(group)
        
        # Generate email content
        email_content = EMAIL_TEMPLATE.format(
            subject=subject,
            inquiry_type=inquiry_type.value,
            inquiry_details=details,
            name=name
        )
        
        # Create probe
        probe = {
            "id": str(uuid.uuid4()),
            "group": group,
            "name": name,
            "email": email,
            "inquiry_type": inquiry_type.value,
            "subject": subject,
            "content": email_content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "seed": self.seed,
                "synthetic": True
            }
        }
        
        return probe
    
    def generate_probe_pair(self, inquiry_type: Optional[InquiryType] = None) -> Tuple[Dict, Dict]:
        """
        Generate a pair of probes, one from each identity group.
        
        Args:
            inquiry_type: Type of inquiry to generate (random if None)
            
        Returns:
            Tuple containing two probe dictionaries
        """
        # Use the same inquiry type for both probes
        if inquiry_type is None:
            inquiry_type = random.choice(list(InquiryType))
        
        # Generate probes
        probe_a = self.generate_probe("group_a", inquiry_type)
        probe_b = self.generate_probe("group_b", inquiry_type)
        
        return probe_a, probe_b
    
    def generate_probe_batch(self, count: int) -> List[Dict]:
        """
        Generate a batch of probes with equal distribution across groups.
        
        Args:
            count: Total number of probes to generate
            
        Returns:
            List of probe dictionaries
        """
        if count % 2 != 0:
            raise ValueError("Probe count must be even to ensure equal distribution")
        
        probes = []
        pairs_count = count // 2
        
        # Generate probe pairs
        for _ in range(pairs_count):
            probe_a, probe_b = self.generate_probe_pair()
            probes.extend([probe_a, probe_b])
        
        return probes


def generate_probes(count: int, seed: Optional[int] = None) -> List[Dict]:
    """
    Convenience function to generate probes.
    
    Args:
        count: Number of probes to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of probe dictionaries
    """
    # Validate that variations meet ethical standards
    ethical_review_hook(IDENTITY_GROUPS)
    
    # Create generator and generate probes
    generator = ProbeGenerator(seed)
    return generator.generate_probe_batch(count)