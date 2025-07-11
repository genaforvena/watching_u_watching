# British Airways (BA) Customer Service Audit Case Definition

## 1. Decision System Characterization
- **System Under Audit**: British Airways (BA) General Customer Service Inquiry Channels (email/web forms)
- **Purpose/Function**: Customer service response management
- **Decision Type**: Responsiveness (response rate, time to response, quality/sentiment)

## 2. Protected Characteristic(s)
- **Characteristic(s)**: Perceived identity (via name as proxy)
- **Rationale**: To test if responsiveness varies based on names associated with different demographics.

## 3. Probe Generation
- **Probe Type**: Standardized customer support inquiry (email/web form)
- **Variation Details**: Utilize `fake_data_helper` to generate synthetic names grouped by perceived demographic association.
- **Template**: Identical inquiry content, varied only by sender name/identity.

## 4. Statistical Parameters
- **Minimum Probes**: [To be determined via power calculation, mimicking realistic volume]
- **Power Calculation**: 80% power to detect differences in responsiveness metrics
- **Confidence Level**: 95%
- **Expected Runtime**: [Varies based on rate limiting and BA response time]

## 5. Validation Metrics
- **Primary Metric**: Response Rate, Time to Response, Response Quality (Sentiment)
- **Bias Threshold**: Significant differences (>X%) in metrics between groups = potential bias
- **False Positive Control**: Standard statistical corrections

## 6. Ethical Safeguards
- **PII Avoidance**: Only synthetic data will be used in probes; raw reply text discarded immediately after analysis.
- **Ethical Review Hook**: `ethical_review_hook()` used prior to probe deployment.
- **Error Handling**: `@rate_limiter` protocol to prevent system disruption.
