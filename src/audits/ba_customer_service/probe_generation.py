"""
Probe Generation Module for British Airways Customer Service Responsiveness Bias Audit

This module implements functions for generating synthetic customer service inquiries
with controlled variations in sender identity while maintaining identical content.
"""

import uuid
import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Assuming these are provided by the framework
from core.utils import fake_data_helper
from core.ethics import ethical_review_hook
from core.decorators import rate_limiter

from .constants import (
    INQUIRY_TEMPLATE,
    VARIATIONS,
    MAX_REQUESTS_PER_DAY,
    REQUEST_INTERVAL_SECONDS
)


@dataclass
class Probe:
    """
    Represents a single customer service inquiry probe.
    """
    probe_id: str
    variation: str  # "western" or "non_western"
    name: str
    content: str
    timestamp: float
    metadata: Dict


def ethical_review_variations(variations: Dict) -> bool:
    """
    Ethical review hook for validating identity variations.
    
    Args:
        variations: Dictionary of variation groups
        
    Returns:
        True if variations pass ethical review, False otherwise
        
    Raises:
        ValueError: If variations fail ethical review
    """
    # Check that we have exactly two variation groups
    if len(variations) != 2:
        raise ValueError("Exactly two variation groups are required for paired testing")
    
    # Check that all variations use synthetic identities
    for group, data in variations.items():
        if not all(fake_data_helper.is_synthetic_name(name) for name in data.get("examples", [])):
            raise ValueError(f"Group '{group}' contains non-synthetic names")
    
    # Validate that the variation groups are balanced
    group_sizes = [len(data.get("examples", [])) for data in variations.values()]
    if len(set(group_sizes)) > 1:
        raise ValueError("Variation groups must have the same number of examples")
    
    return True


@rate_limiter(requests=MAX_REQUESTS_PER_DAY, period=86400)  # 86400 seconds = 24 hours
def generate_probe(variation: str) -> Optional[Probe]:
    """
    Generate a single customer service inquiry probe.
    
    Args:
        variation: The variation group to use ("western" or "non_western")
        
    Returns:
        Probe object or None if generation fails
    """
    if variation not in VARIATIONS:
        raise ValueError(f"Unknown variation: {variation}")
    
    # Get a synthetic name from the specified variation group
    examples = VARIATIONS[variation]["examples"]
    name = fake_data_helper.generate_name(
        gender=None,  # Random gender
        ethnicity=variation,
        examples=examples
    )
    
    # Format the inquiry template with the name
    content = INQUIRY_TEMPLATE.format(name=name)
    
    # Create and return the probe
    return Probe(
        probe_id=str(uuid.uuid4()),
        variation=variation,
        name=name,
        content=content,
        timestamp=time.time(),
        metadata={
            "variation_group": variation,
            "variation_description": VARIATIONS[variation]["description"],
            "synthetic_identity": True,
            "template_used": "standard_inquiry"
        }
    )


def generate_probe_pair() -> Tuple[Probe, Probe]:
    """
    Generate a pair of probes, one from each variation group.
    
    Returns:
        Tuple of two Probe objects, one from each variation group
    """
    western_probe = generate_probe("western")
    
    # Add a small delay between requests to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    non_western_probe = generate_probe("non_western")
    
    return western_probe, non_western_probe


@rate_limiter(requests=MAX_REQUESTS_PER_DAY, period=86400)  # 86400 seconds = 24 hours
def generate_probe_batch(batch_size: int = 10) -> List[Tuple[Probe, Probe]]:
    """
    Generate a batch of probe pairs.
    
    Args:
        batch_size: Number of probe pairs to generate
        
    Returns:
        List of probe pairs
    """
    # First, perform ethical review of the variations
    ethical_review_hook(VARIATIONS)
    
    probe_pairs = []
    for _ in range(batch_size):
        try:
            pair = generate_probe_pair()
            probe_pairs.append(pair)
            
            # Add delay between pairs to respect rate limiting
            time.sleep(REQUEST_INTERVAL_SECONDS / batch_size)
            
        except Exception as e:
            print(f"Error generating probe pair: {e}")
            continue
    
    return probe_pairs


def validate_probe_content(probe: Probe) -> bool:
    """
    Validate that a probe's content meets requirements.
    
    Args:
        probe: Probe to validate
        
    Returns:
        True if probe is valid, False otherwise
    """
    # Check that the probe has all required fields
    required_fields = ["probe_id", "variation", "name", "content", "timestamp"]
    for field in required_fields:
        if not hasattr(probe, field) or getattr(probe, field) is None:
            return False
    
    # Check that the content includes the name
    if probe.name not in probe.content:
        return False
    
    # Check that the content is not too short or too long
    if len(probe.content) < 100 or len(probe.content) > 1000:
        return False
    
    return True