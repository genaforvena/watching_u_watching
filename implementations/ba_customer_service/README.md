# British Airways Customer Service Responsiveness Bias Audit

## Overview
This module implements an automated audit for bias in British Airways (BA) customer service responsiveness, following Issue #25 and the watching_u_watching framework's ethical standards.

## Features
- **Correspondence Testing**: Sends standardized customer service inquiries using synthetic identities.
- **Bias Metrics**: Measures response rate, time to response, and sentiment of replies.
- **Ethical Safeguards**: No real PII is generated or stored; raw reply text is discarded immediately after analysis.
- **Rate Limiting**: Uses a rate limiter to mimic realistic human behavior and prevent system disruption.
- **Extensible**: Easily adaptable for other customer service audits or platforms.

## File Structure
```
ba_customer_service/
├── ba_customer_service_audit.py   # Main audit implementation
├── README.md                     # This documentation
```

## Usage
1. **Configure the audit**: Set the number of probes and demographic groups as needed.
2. **Generate probes**: Use `generate_probes()` to create synthetic customer service inquiries.
3. **Submit probes**: Use `submit_probes()` to simulate sending inquiries and collecting responses.
4. **Analyze results**: Use `analyze_results()` to aggregate and interpret bias metrics.

## Usage Example
```python
from ba_customer_service_audit import BA_CustomerService_Audit

# Step 1: Configure audit with 100 probes and demographic groups
audit = BA_CustomerService_Audit(config={
    "num_probes": 100,
    "demographic_groups": ["GroupA", "GroupB"]
})

# Step 2: Generate synthetic probes
probes = audit.generate_probes(n_pairs=50)

# Step 3: Simulate sending and collecting responses
results = [audit.analyze_response({"text": "Thank you for contacting us.", "response_time": 2.5}) for _ in probes]

# Step 4: Print analyzed results
print(results)
# Example output:
# [
#   {'reply_received': True, 'response_time': 2.5, 'sentiment': 'neutral'},
#   ...
# ]
```

## Ethical Considerations
- Only synthetic/volunteered IDs are used, with embedded markers for traceability.
- No deception about real attributes; all probes are transparently simulated.
- Uninvolved individuals are never targeted.
- All code and data handling strictly follow the watching_u_watching ethical framework and incident response protocol.

## Extending This Audit
- Adapt demographic groups or probe content for other customer service channels.
- Integrate with real email/web form APIs for production use.
- Enhance sentiment analysis with NLP libraries for more robust metrics.

## References
- [ETHICS.md](../../ETHICS.md)
- [Framework Extension Guide](../../how_to_apply_guide/extending_framework.md)
- [Issue #25](https://github.com/genaforvena/watching_u_watching/issues/25)
