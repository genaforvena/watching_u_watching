# British Airways Customer Service Responsiveness Bias Audit

## 1. Decision System Characterization
- **System Under Audit**: British Airways Customer Service
- **Purpose/Function**: Customer inquiry response system
- **Decision Type**: Response prioritization and quality

## 2. Protected Characteristic(s)
- **Characteristic(s)**: Perceived identity (via name as proxy)
- **Rationale**: Names can signal demographic information that may influence service quality

## 3. Probe Generation
- **Probe Type**: Standardized customer support inquiry via email/web form
- **Variation Details**:
  - Group A: Names associated with perceived British/Western identity
  - Group B: Names associated with perceived non-Western identity
- **Template**:
  ```
  Subject: Inquiry about [INQUIRY_TYPE]
  
  Dear British Airways Customer Service,
  
  I hope this message finds you well. I am writing to inquire about [SPECIFIC_INQUIRY] for my upcoming travel.
  
  [INQUIRY_DETAILS]
  
  I would greatly appreciate your assistance with this matter.
  
  Thank you for your time and consideration.
  
  Best regards,
  [NAME]
  ```

## 4. Statistical Parameters
- **Minimum Probes**: 100 pairs (50 per group)
- **Power Calculation**: 80% power to detect 15% difference in response rate
- **Confidence Level**: 95%
- **Expected Runtime**: 14 days (to account for response time)

## 5. Validation Metrics
- **Primary Metrics**: 
  1. Response Rate: Percentage of inquiries receiving a response
  2. Response Time: Average time to first response
  3. Response Quality: Sentiment analysis score of responses
- **Bias Threshold**: 
  - >15% difference in response rate = significant bias
  - >24 hour difference in average response time = significant bias
  - >0.2 difference in sentiment score = significant bias
- **False Positive Control**: Benjamini-Hochberg correction for multiple comparisons

## 6. Ethical Safeguards
- **PII Avoidance**: Only synthetic identities used, no real customer data
- **Rate Limiting**: Maximum 10 inquiries per day to prevent system disruption
- **Ethical Review Hook**: `ethical_review_hook()` validates all probe content before sending
- **Data Retention**: Response content discarded after sentiment analysis