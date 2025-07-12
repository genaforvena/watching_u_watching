"""
Constants for British Airways Customer Service Responsiveness Bias Audit

This module contains all constants used in the BA customer service audit,
including templates, inquiry types, and configuration parameters.
"""

from enum import Enum
from typing import Dict, List

# Compatibility version
COMPATIBILITY_VERSION = 1.2

# Statistical parameters
MIN_PROBES = 100  # 50 per group
CONFIDENCE_LEVEL = 0.95
POWER_LEVEL = 0.80
EFFECT_SIZE = 0.15  # 15% difference in response rate

# Rate limiting parameters
MAX_INQUIRIES_PER_DAY = 10
RATE_LIMIT_PERIOD = 86400  # 24 hours in seconds

# Bias thresholds
RESPONSE_RATE_THRESHOLD = 0.15  # 15% difference
RESPONSE_TIME_THRESHOLD = 24 * 60 * 60  # 24 hours in seconds
SENTIMENT_SCORE_THRESHOLD = 0.2  # 0.2 difference in sentiment score (range -1 to 1)

# Inquiry types
class InquiryType(Enum):
    BOOKING = "booking information"
    BAGGAGE = "baggage allowance"
    SPECIAL_ASSISTANCE = "special assistance"
    FLIGHT_CHANGE = "flight change options"
    LOYALTY_PROGRAM = "Executive Club membership"


# Inquiry templates
INQUIRY_TEMPLATES = {
    InquiryType.BOOKING: {
        "subject": "Inquiry about booking information",
        "details": "I recently made a booking (reference number: [BOOKING_REF]) and would like to confirm "
                  "the details of my reservation. Could you please provide information about my seat assignment "
                  "and meal preferences? Additionally, I would like to know if there are any documents I need "
                  "to prepare before my flight."
    },
    InquiryType.BAGGAGE: {
        "subject": "Inquiry about baggage allowance",
        "details": "I am planning to travel with British Airways next month and would like to clarify "
                  "the baggage allowance for my flight. I will be traveling with [BAGGAGE_ITEMS] and "
                  "would like to know if this falls within the standard allowance or if I need to purchase "
                  "additional baggage. Could you also inform me about any restrictions for carry-on items?"
    },
    InquiryType.SPECIAL_ASSISTANCE: {
        "subject": "Inquiry about special assistance",
        "details": "I will be traveling on [FLIGHT_DATE] and require special assistance due to [ASSISTANCE_REASON]. "
                  "Could you please provide information on how to arrange this service? I would also like to know "
                  "what documentation I need to provide and how early I should arrive at the airport."
    },
    InquiryType.FLIGHT_CHANGE: {
        "subject": "Inquiry about flight change options",
        "details": "I need to change my upcoming flight scheduled for [FLIGHT_DATE]. Could you please "
                  "inform me about the available options and any associated fees? I would prefer to "
                  "reschedule to [NEW_DATE] if possible. Is this change something I can make online, "
                  "or do I need to speak with a representative?"
    },
    InquiryType.LOYALTY_PROGRAM: {
        "subject": "Inquiry about Executive Club membership",
        "details": "I am interested in learning more about the British Airways Executive Club program. "
                  "Could you please provide information about the benefits, how to earn and redeem Avios points, "
                  "and the different membership tiers? I travel approximately [TRAVEL_FREQUENCY] and would like "
                  "to know which tier would be most suitable for me."
    }
}

# Identity groups for testing
IDENTITY_GROUPS = {
    "group_a": {  # British/Western perceived names
        "names": [
            "James Wilson",
            "Emma Thompson",
            "William Parker",
            "Charlotte Davies",
            "Oliver Smith",
            "Sophie Johnson",
            "Henry Williams",
            "Elizabeth Brown",
            "George Taylor",
            "Victoria Mitchell"
        ],
        "emails": [
            "james.wilson@example.com",
            "emma.thompson@example.com",
            "william.parker@example.com",
            "charlotte.davies@example.com",
            "oliver.smith@example.com",
            "sophie.johnson@example.com",
            "henry.williams@example.com",
            "elizabeth.brown@example.com",
            "george.taylor@example.com",
            "victoria.mitchell@example.com"
        ]
    },
    "group_b": {  # Non-Western perceived names
        "names": [
            "Mohammed Ahmed",
            "Fatima Khan",
            "Raj Patel",
            "Aisha Mahmood",
            "Chen Wei",
            "Priya Singh",
            "Kwame Osei",
            "Mei Lin",
            "Abdul Rahman",
            "Zara Hussain"
        ],
        "emails": [
            "mohammed.ahmed@example.com",
            "fatima.khan@example.com",
            "raj.patel@example.com",
            "aisha.mahmood@example.com",
            "chen.wei@example.com",
            "priya.singh@example.com",
            "kwame.osei@example.com",
            "mei.lin@example.com",
            "abdul.rahman@example.com",
            "zara.hussain@example.com"
        ]
    }
}

# Email template
EMAIL_TEMPLATE = """Subject: {subject}

Dear British Airways Customer Service,

I hope this message finds you well. I am writing to inquire about {inquiry_type} for my upcoming travel.

{inquiry_details}

I would greatly appreciate your assistance with this matter.

Thank you for your time and consideration.

Best regards,
{name}
"""

# Placeholder values for templates
PLACEHOLDER_VALUES = {
    "BOOKING_REF": ["ABC123", "XYZ789", "DEF456", "GHI789", "JKL012"],
    "BAGGAGE_ITEMS": [
        "one large suitcase and a laptop bag",
        "two medium suitcases",
        "a sports equipment bag",
        "fragile items",
        "medical equipment"
    ],
    "FLIGHT_DATE": [
        "15th of next month",
        "20th of next month",
        "first week of next month",
        "end of next month",
        "middle of next month"
    ],
    "ASSISTANCE_REASON": [
        "mobility limitations",
        "traveling with an infant",
        "visual impairment",
        "dietary restrictions",
        "medical condition"
    ],
    "NEW_DATE": [
        "one week later",
        "the following weekend",
        "three days earlier",
        "the same day next week",
        "the end of the month"
    ],
    "TRAVEL_FREQUENCY": [
        "3-4 times per year",
        "monthly for business",
        "twice yearly for holidays",
        "6-8 times annually",
        "quarterly for both business and leisure"
    ]
}