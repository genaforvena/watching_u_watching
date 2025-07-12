# Constants for British Airways Customer Service Audit

# Define the compatibility version
compatibility_version = 1.2

# Define the minimum number of probes required for statistical validity
MIN_PROBES = 100  # pairs (200 total inquiries)

# Define the variations for testing
VARIATIONS = {
    'majority': {
        'demographic': 'perceived_majority',
        'name_origin': 'british'
    },
    'minority': {
        'demographic': 'perceived_minority',
        'name_origin': 'middle_eastern'
    }
}

# Define inquiry templates
INQUIRY_TEMPLATE = """
Dear British Airways Customer Service,

I am planning to travel from {origin} to {destination} on {date} and have a question about {service_type}.

{inquiry_text}

Thank you for your assistance.

Sincerely,
{name}
"""

# Define standard inquiry types
INQUIRY_TYPES = [
    {
        'service_type': 'baggage allowance',
        'inquiry_text': 'Could you please confirm the checked baggage allowance for my flight? I would like to know if I can bring an additional bag and what the cost would be.'
    },
    {
        'service_type': 'seat selection',
        'inquiry_text': 'I would like to know how I can select my seat in advance. Is there a fee for this service, and if so, what are the options and prices?'
    },
    {
        'service_type': 'flight changes',
        'inquiry_text': 'I may need to change my flight date. Could you please explain the process and any fees that might apply for making changes to my booking?'
    },
    {
        'service_type': 'special assistance',
        'inquiry_text': 'I require special assistance at the airport. Could you please provide information on how to arrange this and what services are available?'
    }
]

# Define common flight routes for realistic inquiries
FLIGHT_ROUTES = [
    {'origin': 'London', 'destination': 'New York'},
    {'origin': 'Manchester', 'destination': 'Dubai'},
    {'origin': 'Edinburgh', 'destination': 'Paris'},
    {'origin': 'Glasgow', 'destination': 'Amsterdam'},
    {'origin': 'London', 'destination': 'Tokyo'},
    {'origin': 'Birmingham', 'destination': 'Barcelona'}
]
