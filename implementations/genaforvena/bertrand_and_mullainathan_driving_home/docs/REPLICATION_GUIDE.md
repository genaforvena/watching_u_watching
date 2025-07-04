# How to Replicate This Audit
1. **Set Up Probes**:
   ```bash
   python implementation/probe_generator.py --pairs 50 --output probes.csv
   ```

2. **Send Probes** (Rate-Limited):
   ```bash
   python implementation/email_handler.py --input probes.csv
   ```

3. **Analyze Results**:
   ```bash
   python implementation/analysis.py --data responses.csv
   ```

## Ethical Safeguards
- All personal data is auto-sanitized using:
  ```python
  re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', 'Institution', text)
  ```
- Never run more than 5 probes/day per institution
