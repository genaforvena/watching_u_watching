# Automated Paired Testing for Systemic Bias in the Berlin Housing Market

## Landlord Categorization & Data Minimization

This system automatically categorizes each property as belonging to one of the **top 5 Berlin corporate landlords** (Deutsche Wohnen, Vonovia, Adler Group, Covivio, Grand City Properties) or as **"other"**. For "other" landlords, no identifying information is stored—only the label "other" is used for analysis. This ensures:

- **Maximum impact**: Systemic bias can be detected at the largest institutions.
- **Full privacy**: No PII or identifying info is ever stored for any individual or non-corporate landlord.
- **Broad coverage**: All listings are processed, but only the top 5 are named; all others are anonymized.

## Data Minimization & Privacy-by-Design

- **No email content or PII is ever stored**—not even in redacted form. Only minimal metadata (reply received, is positive response, timestamp, response type) is extracted in-memory and persisted.
- **Landlord category** is the only property-level label: one of the top 5 by name, or "other".

This approach exceeds GDPR and research ethics requirements, and is aligned with the "NO HARM is above all" principle.


This implementation provides automated monitoring and application submission for rental properties on Immobilienscout24.de to detect systemic bias through paired testing methodology.

## Overview

This system implements the methodology described in Issue #12, automatically:

1. **Monitoring**: Continuously monitors Immobilienscout24.de for new rental property postings
2. **Application Generation**: Creates applications using predefined German templates for two personas:
   - Mohammed Abasi (Arabic/Middle Eastern name)
   - Franz Müller (German name)
3. **Submission**: Automatically submits applications through the platform's standard processes
4. **PII Redaction**: Transforms all received email content into random symbols while maintaining word length for privacy protection

## Key Features

- **No LLM Generation**: Applications use static, predefined German templates as specified in the requirements
- **Strict PII Protection**: All received email content is transformed into random symbols maintaining word length
- **Ethical Compliance**: Follows the watching_u_watching project's "no harm" principle
- **Automated Monitoring**: Continuously scans for new rental listings based on configurable criteria
- **Paired Testing**: Systematically varies only the applicant name while keeping all other variables constant

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Configure monitoring parameters
cp config.example.json config.json
# Edit config.json with your search criteria

# Run the monitoring and application system
python src/main.py

# View analysis results
python src/analyze_responses.py
```

## Directory Structure

```
.
├── README.md
├── requirements.txt
├── config.example.json
├── src/
│   ├── main.py                 # Main orchestration script
│   ├── property_monitor.py     # Immobilienscout24.de monitoring
│   ├── application_generator.py # Generate applications from templates
│   ├── submission_system.py    # Submit applications to platform
│   ├── pii_redactor.py        # PII redaction with random symbols
│   ├── data_storage.py        # Store results and metadata
│   └── analyze_responses.py    # Analysis and reporting
└── tests/
    ├── test_property_monitor.py
    ├── test_application_generator.py
    ├── test_pii_redactor.py
    └── test_integration.py
```

## Ethical Considerations


This implementation strictly adheres to ethical research principles:

- **Fictitious Personas**: Uses only fictional identities with no real PII
- **Privacy Protection**: All received content is immediately discarded after extracting minimal metadata; no PII or content is ever stored
- **Landlord Anonymization**: For all but the top 5, only the label "other" is stored—no identifying info
- **Transparency**: Open-source methodology allowing independent verification
- **Research Purpose**: Legitimate academic/policy research into systemic bias
- **No Harm Principle**: Designed to detect and expose discrimination, not cause harm

## Legal Compliance

This system is designed to comply with:
- German Anti-Discrimination Laws (AGG)
- EU GDPR requirements through strict PII redaction
- Platform Terms of Service through legitimate application processes
- Academic research exemptions for bias detection studies

## Configuration

Key configuration parameters:
- Search criteria (location, size, price range)
- Monitoring frequency and rate limiting
- Application templates customization
- PII redaction settings
- Data retention policies

See `config.example.json` for detailed configuration options.