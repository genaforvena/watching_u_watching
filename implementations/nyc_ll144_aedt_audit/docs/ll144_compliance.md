# NYC Local Law 144 Compliance Guide

## Overview of NYC Local Law 144

NYC Local Law 144 (LL144) requires employers and employment agencies to conduct independent bias audits of Automated Employment Decision Tools (AEDTs) used in hiring and promotion decisions. This guide outlines how the `watching_u_watching` framework can be used to conduct audits that comply with LL144 requirements.

## Key LL144 Requirements

### Definition of AEDT

Under LL144, an AEDT is defined as:

> "Any computational process, derived from machine learning, statistical modeling, data analytics, or artificial intelligence, that issues simplified output, including a score, classification, or recommendation, that is used to substantially assist or replace discretionary decision making for making employment decisions that impact natural persons."

### Bias Audit Requirements

LL144 requires:

1. An **independent bias audit** conducted no more than one year prior to use of the AEDT
2. A **summary of results** made publicly available on the employer or employment agency's website
3. Testing for **disparate impact** based on race/ethnicity and sex/gender

### Disclosure Requirements

Employers must provide notice to candidates:

1. That an AEDT will be used in the assessment or evaluation
2. The job qualifications and characteristics that the AEDT will assess
3. The type of data collected for the AEDT and the source of such data

## How This Implementation Ensures Compliance

### 1. Independent Bias Audit

This implementation provides a truly independent bias audit by:

- Using an **open-source methodology** that can be verified by anyone
- Providing **transparent code** for probe generation, submission, and analysis
- Enabling **community oversight** through the open-source development model
- Eliminating **commercial conflicts of interest** that might temper audit rigor

### 2. Testing for Disparate Impact

The implementation tests for disparate impact by:

- Generating **paired applications** that differ only in protected characteristics
- Controlling all **non-test variables** to isolate the effect of protected characteristics
- Calculating **disparate impact ratios** as required by LL144
- Testing for **statistical significance** of observed differences
- Supporting **intersectional analysis** of multiple protected characteristics

### 3. Summary of Results

The implementation generates LL144-compliant summary reports that include:

- **Disparate impact ratios** for each protected characteristic
- **Statistical significance** of observed differences
- **Confidence intervals** for impact ratios
- **Sample sizes** and other relevant statistical information
- **Visualization** of results for clear communication

## Audit Methodology

### Protected Characteristics

The implementation tests for bias based on:

1. **Race/Ethnicity**: Using name-based proxies and explicit demographic information
2. **Sex/Gender**: Using name-based proxies, pronouns, and explicit demographic information
3. **Intersectional**: Testing for bias at the intersection of multiple protected characteristics

### Disparate Impact Analysis

The implementation calculates disparate impact using:

1. **Selection Rate Calculation**: For each group, calculate the selection rate as the number of candidates selected divided by the number of candidates in the group
2. **Impact Ratio Calculation**: Calculate the ratio of the selection rate for the protected group to the selection rate for the reference group
3. **4/5ths Rule Application**: Apply the 80% rule (4/5ths rule) to determine adverse impact
4. **Statistical Significance Testing**: Test for statistical significance of observed differences
5. **Confidence Interval Calculation**: Calculate confidence intervals for impact ratios

### Report Generation

The implementation generates reports that include:

1. **Audit Methodology**: Description of the audit methodology
2. **Sample Characteristics**: Description of the synthetic applications used
3. **Results**: Disparate impact ratios and statistical significance
4. **Limitations**: Discussion of limitations and caveats
5. **Recommendations**: Suggestions for mitigating identified bias

## Practical Implementation Steps

### 1. Configure the Audit

```json
{
  "probe_generation": {
    "protected_characteristics": {
      "race_ethnicity": true,
      "sex_gender": true,
      "intersectional": true
    }
  },
  "analysis": {
    "metrics": {
      "disparate_impact_ratio": true,
      "statistical_significance": true,
      "confidence_intervals": true
    },
    "output_format": "ll144_compliant"
  }
}
```

### 2. Generate Synthetic Applications

The implementation generates synthetic applications that:

- Vary only in protected characteristics
- Control for all other variables
- Are realistic and representative
- Cover a range of job types and qualifications

### 3. Submit Applications to AEDT

The implementation submits applications through:

- Web forms
- APIs
- Email
- Other interfaces as needed

### 4. Collect and Analyze Responses

The implementation:

- Collects responses from the AEDT
- Extracts relevant metrics
- Calculates disparate impact ratios
- Tests for statistical significance
- Generates LL144-compliant reports

## Legal Considerations

### Compliance with LL144

This implementation is designed to comply with LL144 requirements, but users should:

- Consult with legal counsel to ensure compliance with all aspects of LL144
- Stay informed about updates to LL144 and related regulations
- Document the audit process and results for potential regulatory review

### Privacy Considerations

The implementation:

- Uses only synthetic data
- Implements strict PII handling
- Complies with relevant privacy regulations
- Minimizes data collection and retention

## Conclusion

This implementation provides a robust framework for conducting independent bias audits of AEDTs in compliance with NYC Local Law 144. By using this open-source, transparent methodology, employers and employment agencies can ensure that their AEDTs are being properly audited for bias, while also benefiting from the rigor and independence that comes from community-driven development.

## References

- [NYC Local Law 144 Text](https://www.nyc.gov/assets/dcas/downloads/pdf/agencies/local_law_144.pdf)
- [NYC Department of Consumer and Worker Protection Rules](https://rules.cityofnewyork.us/rule/automated-employment-decision-tools/)
- [EEOC Uniform Guidelines on Employee Selection Procedures](https://www.govinfo.gov/content/pkg/CFR-2019-title29-vol4/xml/CFR-2019-title29-vol4-part1607.xml)