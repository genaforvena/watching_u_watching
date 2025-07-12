# British Airways Customer Service Responsiveness Bias Audit

## 1. Decision System Characterization
- **System Under Audit**: British Airways Customer Service Inquiry Channels
- **Purpose/Function**: Responding to customer inquiries and support requests
- **Decision Type**: Response provision (timing, quality, and whether a response is provided)

## 2. Protected Characteristic(s)
- **Characteristic(s)**: Perceived identity (via name as proxy)
- **Rationale**: Names can signal perceived ethnicity, nationality, or cultural background, which may unconsciously influence customer service responsiveness

## 3. Probe Generation
- **Probe Type**: Standardized customer service inquiry via email/web form
- **Variation Details**:
  - Group A: Western-sounding names (e.g., "James Wilson", "Emma Thompson")
  - Group B: Non-Western-sounding names (e.g., "Mohammed Ahmed", "Aisha Khan")
- **Template**:
  ```
  Subject: Question about flight booking options
  
  Dear British Airways Customer Service,
  
  I am planning to book a flight from London to New York in the coming months and have a question about your booking options.
  
  Could you please provide information about the different fare classes available and what amenities are included with each? I'm particularly interested in understanding the differences between your economy and premium economy offerings.
  
  Thank you for your assistance.
  
  Sincerely,
  $NAME
  ```

## 4. Statistical Parameters
- **Minimum Probes**: 100 pairs (50 per group)
- **Power Calculation**: 80% power to detect 15% difference in response rate
- **Confidence Level**: 95%
- **Expected Runtime**: 14 days (to account for response time variations)

## 5. Validation Metrics
- **Primary Metrics**:
  1. **Response Rate**: Percentage of inquiries receiving a response (Group A vs. Group B)
  2. **Response Time**: Average time elapsed between inquiry submission and response receipt
  3. **Response Quality**: Sentiment analysis score of response content
- **Bias Threshold**: 
  - Response Rate: >10% difference = significant bias
  - Response Time: >24 hour difference = significant bias
  - Response Quality: >0.2 sentiment score difference = significant bias
- **False Positive Control**: Benjamini-Hochberg procedure with α = 0.05

## 6. Ethical Safeguards
- **PII Avoidance**: Only synthetic identities generated via fake_data_helper
- **Rate Limiting**: Maximum 5 inquiries per day to prevent system disruption
- **Ethical Review Hook**: `validate_identity_variations()` to ensure:
  1. No real customer identities are used
  2. Inquiry content is identical except for sender information
  3. Inquiries are reasonable and do not waste customer service resources
- **Data Handling**: Raw response text discarded immediately after sentiment analysis
- **Error Handling**: Graceful termination on HTTP 429 (Too Many Requests)