"""
Constants for British Airways Customer Service Responsiveness Bias Audit

This module defines constants used throughout the audit implementation,
including variation definitions, templates, and configuration parameters.
"""

from enum import Enum
from typing import Dict, Any

# Framework compatibility version
COMPATIBILITY_VERSION = 1.2

# Statistical parameters
MIN_PROBES = 100  # 50 per group
CONFIDENCE_LEVEL = 0.95
POWER_LEVEL = 0.80
EFFECT_SIZE = 0.15  # 15% difference in response rate
BIAS_THRESHOLD = {
    "response_rate": 0.10,  # 10% difference
    "response_time": 24,    # 24 hours difference
    "sentiment": 0.20       # 0.2 sentiment score difference
}

# Rate limiting parameters
MAX_REQUESTS_PER_DAY = 5
REQUEST_INTERVAL_SECONDS = 17280  # 4.8 hours (to spread 5 requests over 24 hours)

# Inquiry template
INQUIRY_TEMPLATE = """Subject: Question about flight booking options

Dear British Airways Customer Service,

I am planning to book a flight from London to New York in the coming months and have a question about your booking options.

Could you please provide information about the different fare classes available and what amenities are included with each? I'm particularly interested in understanding the differences between your economy and premium economy offerings.

Thank you for your assistance.

Sincerely,
{name}
"""

# Variation definitions
VARIATIONS = {
    "western": {
        "description": "Western-sounding names",
        "examples": ["James Wilson", "Emma Thompson", "Robert Johnson", "Sarah Davis"]
    },
    "non_western": {
        "description": "Non-Western-sounding names",
        "examples": ["Mohammed Ahmed", "Aisha Khan", "Wei Zhang", "Fatima Al-Farsi"]
    }
}

# Contact channels
CONTACT_CHANNELS = {
    "email": "customer.service@ba.com",
    "web_form": "https://www.britishairways.com/travel/contact-form/public/en_gb"
}

# Response analysis parameters
class SentimentCategory(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"

SENTIMENT_THRESHOLDS = {
    SentimentCategory.NEGATIVE: -0.05,
    SentimentCategory.NEUTRAL: 0.05,
    SentimentCategory.POSITIVE: float('inf')
}

# Audit metadata
AUDIT_METADATA = {
    "name": "British Airways Customer Service Responsiveness Bias Audit",
    "version": "1.0.0",
    "description": "Audit to detect potential bias in British Airways customer service responsiveness",
    "authors": ["Watching U Watching Framework Team"],
    "contact": "framework@example.org",
    "documentation": "https://github.com/genaforvena/watching_u_watching/audit_cases/BA_CustomerService_Audit.md"
}