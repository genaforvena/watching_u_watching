# NYC Local Law 144 AEDT Audit Implementation

## Overview

This implementation provides a comprehensive framework for conducting transparent and adversarial audits of Automated Employment Decision Tools (AEDTs) in compliance with NYC Local Law 144 (LL144). The framework leverages the `watching_u_watching` methodology to generate synthetic employment applications, submit them to AEDTs, collect responses, and analyze results for disparate impact.

## Key Features

- **LL144-Specific Probe Templates**: Pre-configured templates for common AEDT inputs (resumes, application forms)
- **Disparate Impact Analysis**: Automated calculation of disparate impact ratios and other metrics required by LL144
- **Protected Class Testing**: Support for testing bias across race/ethnicity, sex/gender, and intersectional groups
- **Scalable Testing**: Ability to generate thousands of controlled test cases to detect subtle biases
- **Privacy-Preserving**: Strong safeguards to protect PII and ensure ethical operation
- **Open-Source Transparency**: Fully transparent methodology for independent verification

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages (see `requirements.txt`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/watching_u_watching.git

# Navigate to the implementation directory
cd watching_u_watching/implementations/nyc_ll144_aedt_audit

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example configuration file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` to configure your audit parameters:
   - Target AEDT systems
   - Protected characteristics to test
   - Number of probe pairs to generate
   - Output format preferences

### Running an Audit

```bash
# Run a demonstration with sample data
python demo.py

# Run a full audit
python src/main.py --config config.json
```

## Components

- **AEDT Probe Generator**: Creates synthetic employment applications with controlled variations
- **Submission System**: Submits applications to AEDTs through various interfaces
- **Response Collector**: Collects and processes responses while preserving privacy
- **LL144 Metrics Calculator**: Calculates disparate impact ratios and other required metrics
- **Analysis Tools**: Analyzes results and generates LL144-compliant reports

## Documentation

- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md): Detailed description of the implementation
- [LL144 Compliance Guide](./docs/ll144_compliance.md): Guide to ensuring compliance with LL144 requirements
- [Ethical Considerations](./docs/ethical_considerations.md): Discussion of ethical considerations for AEDT auditing

## Contributing

Contributions are welcome! Please see the [Contributing Guide](../../CONTRIBUTING.md) for more information.

## License

This project is licensed under the terms of the CC0 (Public Domain) license.