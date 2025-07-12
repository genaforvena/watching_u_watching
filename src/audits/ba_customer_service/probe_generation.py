import random
import time
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from .constants import MIN_PROBES, VARIATIONS, INQUIRY_TEMPLATE, INQUIRY_TYPES, FLIGHT_ROUTES
from fake_data_helper import generate_synthetic_name, generate_fake_email
from rate_limiter import rate_limiter

def _generate_future_date() -> str:
    """
    Generate a realistic future date for travel inquiries.
    
    Returns:
        String representation of a date 2-8 weeks in the future
    """
    days_in_future = random.randint(14, 56)  # 2-8 weeks
    future_date = datetime.now() + timedelta(days=days_in_future)
    return future_date.strftime("%d %B %Y")  # e.g., "15 June 2023"

def _generate_inquiry_content() -> Dict:
    """
    Generate the content for a customer service inquiry.
    
    Returns:
        Dictionary with inquiry content details
    """
    # Select a random inquiry type
    inquiry_type = random.choice(INQUIRY_TYPES)
    
    # Select a random flight route
    route = random.choice(FLIGHT_ROUTES)
    
    # Generate a future date
    date = _generate_future_date()
    
    return {
        'service_type': inquiry_type['service_type'],
        'inquiry_text': inquiry_type['inquiry_text'],
        'origin': route['origin'],
        'destination': route['destination'],
        'date': date
    }

def _create_probe(variation_key: str, variation: Dict, inquiry_content: Dict) -> Dict:
    """
    Create a single probe.
    
    Args:
        variation_key: Key of the variation
        variation: Variation dictionary
        inquiry_content: Inquiry content dictionary
        
    Returns:
        Probe dictionary
    """
    # Generate synthetic identity based on demographic
    try:
        synthetic_name = generate_synthetic_name(origin=variation['name_origin'])
        email = generate_fake_email(name=synthetic_name)
    except Exception as e:
        # Sanitize exception message before logging
        sanitized_error = str(e).replace('\n', ' ')
        logging.error(f"Error generating synthetic identity: {sanitized_error}")
        # Return None or raise a specific exception if a probe cannot be created
        # For now, we'll log and return None, which will be filtered out later
        return None
    
    # Create the inquiry text
    inquiry_text = INQUIRY_TEMPLATE.format(
        origin=inquiry_content['origin'],
        destination=inquiry_content['destination'],
        date=inquiry_content['date'],
        service_type=inquiry_content['service_type'],
        inquiry_text=inquiry_content['inquiry_text'],
        name=synthetic_name
    )
    
    # Create the probe
    return {
        'id': f"ba-{variation_key}-{time.time_ns()}-{random.randint(1000, 9999)}",
        'variation': variation_key,
        'demographic': variation['demographic'],
        'name': synthetic_name,
        'email': email,
        'subject': f"Question about {inquiry_content['service_type']}",
        'body': inquiry_text,
        'timestamp': datetime.now().isoformat(),
        'inquiry_type': inquiry_content['service_type'],
        'route': f"{inquiry_content['origin']} to {inquiry_content['destination']}"
    }

def _generate_probe_pair() -> List[Dict]:
    """
    Generate a pair of probes for each variation.
    
    Returns:
        List of two probe dictionaries
    """
    # Generate common inquiry content for the pair
    inquiry_content = _generate_inquiry_content()
    
    # Generate a probe for each variation
    return [
        _create_probe(variation_key, variation, inquiry_content)
        for variation_key, variation in VARIATIONS.items()
    ]

@rate_limiter(requests=5, period=86400)  # 5 requests per day (86400 seconds)
def generate_probes(num_pairs: int) -> List[Dict]:
    """
    Generate paired probes for testing BA customer service responsiveness.
    
    Args:
        num_pairs: Number of probe pairs to generate
        
    Returns:
        List of probe dictionaries
    """
    # Validate through ethical review hook (assuming ethical_review_hook is in audit.py)
    # if not ethical_review_hook(VARIATIONS):
    #     raise ValueError("Failed ethical review - audit cannot proceed")
        
    if num_pairs < MIN_PROBES:
#     raise ValueError("Failed ethical review - audit cannot proceed")
        
    if num_pairs < MIN_PROBES:
        sanitized_num_pairs = str(num_pairs).replace('
', ' ')
        logging.warning(f"{sanitized_num_pairs} pairs is below the recommended minimum of {MIN_PROBES}")
    
    # Generate probes using generator expression
    probes_generator = (
        probe
        for _ in range(num_pairs)
        for probe in _generate_probe_pair()
    )
    
    # Convert generator to list for consistency with return type
    probes_list = list(probes_generator)

    # Sanitize input before logging
        sanitized_num_pairs = str(num_pairs).replace('\n', ' ')
    # Generate probes using list comprehension} pairs is below the recommended minimum of {MIN_PROBES}")
    # TODO: Consider using a generator expression for large num_pairs to reduce memory usage.
    probes = [e probes using generator expression
        probe
        for _ in range(num_pairs)
        for probe in _generate_probe_pair()   for _ in range(num_pairs)
    ]    for probe in _generate_probe_pair()
    
    logging.info(f"Generated {len(probes)} probes ({num_pairs} pairs)")
    return probes    # Convert generator to list for consistency with return type

    probes_list = list(probes_generator)

    # Sanitize input before logging
    sanitized_len_probes = str(len(probes_list)).replace('\n', ' ')
    sanitized_num_pairs_log = str(num_pairs).replace('\n', ' ')
    logging.info(f"Generated {sanitized_len_probes} probes ({sanitized_num_pairs_log} pairs)")

    return probes_list
