# British Airways Customer Service Responsiveness Bias Audit

## 1. Decision System Characterization

- **System Under Audit**: British Airways (BA) Customer Service Inquiry Channels
- **Purpose/Function**: Handling customer inquiries and support requests
- **Decision Type**: Response quality and timing (continuous)

## 2. Protected Characteristic(s)

- **Characteristic(s) to Test**: Perceived identity (via name as proxy)
- **Rationale**: Names can signal demographic information that may unconsciously influence service quality
- **Proxy Variables**: Customer names with different perceived demographic associations

## 3. Probe Generation Strategy

- **Probe Type**: Standardized email/web form inquiries
- **Variation Details**:
  - Group A: Names associated with perceived majority demographic
  - Group B: Names associated with perceived minority demographic
- **Control Variables**:
  - Inquiry content (identical except for sender name)
  - Time of day (randomized but balanced between groups)
  - Type of inquiry (standard customer service questions)
- **Template**:

  ```text
  Subject: Question about [specific service]
  
  Dear British Airways Customer Service,
  
  I am planning to travel from [origin] to [destination] on [date] and have a question about [specific service].
  
  [Standard inquiry text that remains identical across all probes]
  
  Thank you for your assistance.
  
  Sincerely,
  [Name]
  ```

## 4. Statistical Parameters

- **Minimum Probes**: 100 pairs (200 total inquiries)
- **Power Calculation**: 80% power to detect 15% difference in response rate or timing
- **Confidence Level**: 95%
- **Expected Runtime**: 3 weeks (accounting for response delays)

## 5. Validation Metrics

- **Primary Metrics**:
  1. Response Rate: Percentage of inquiries receiving any response
  2. Time to Response: Average hours/days until first response
  3. Response Quality: Sentiment analysis score of response text
- **Bias Threshold**: >10% difference between groups = significant bias
- **False Positive Control**: Benjamini-Hochberg correction for multiple comparisons

## 6. Ethical Safeguards

- **PII Avoidance**:
  - Only synthetic identities used
  - All response content discarded after sentiment analysis
  - No storage of actual BA employee information
- **Rate Limiting**: Maximum 5 inquiries per day to prevent system disruption
- **Ethical Review Hook**: `ethical_review_hook()` to ensure ethical use of name-based testing
- **Error Handling**: Automatic halt if any PII is accidentally collected
