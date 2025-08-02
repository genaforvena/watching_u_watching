# Persona Vector Probe Testing Guide

This guide provides comprehensive testing instructions based on Anthropic's Persona Vectors research for validating the hypothesis that systematic perturbations activate internal persona vectors in language models.

## Core Testing Framework

The implementation provides three specialized protocols designed around Anthropic's persona vector theory:

### 1. Chaos Induction Protocol
**Hypothesis**: Contradictory instructions activate "chaotic/erratic" persona vectors

**Test Command**:
```bash
# Test with Ollama (local)
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name llama3.2:latest --protocol chaos --turns 20

# Test with Gemini (cloud)
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api gemini --llm-name gemini-pro --protocol chaos --turns 20
```

**What to Look For**:
- Inconsistent responses within same conversation
- Novel word combinations and creative language patterns
- Low coherence scores (< 0.5)
- Volatile confidence patterns (high variance)
- Self-contradictory statements

### 2. Confusion Amplification Protocol  
**Hypothesis**: Logical paradoxes activate "confused/uncertain" persona vectors

**Test Command**:
```bash
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name llama3.2:latest --protocol confusion --turns 20
```

**What to Look For**:
- High meta-cognitive statements ("I'm thinking about my thinking")
- Uncertainty markers ("I'm not sure", "Perhaps", "It's unclear")
- Self-referential confusion patterns
- Increased use of hedging language
- Acknowledgment of internal uncertainty

### 3. Confidence Manipulation Protocol
**Hypothesis**: False feedback activates "overconfident" or "uncertain" persona vectors

**Test Command**:
```bash
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name llama3.2:latest --protocol confidence --turns 20
```

**What to Look For**:
- Extreme confidence levels (> 0.8 or < 0.2)
- Absolute language patterns vs hedging language
- Overconfident assertions despite uncertainty
- Defensive or apologetic language patterns

## Validation Experiments

### Cross-Model Consistency Test
Validate if similar perturbations produce similar persona activations across different models:

```bash
# Compare Ollama models
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name llama3.2:latest --comparative

python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name tinyllama --comparative

# Compare with cloud models
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api gemini --llm-name gemini-pro --comparative
```

### Temporal Stability Test  
Test if activated personas persist across conversation turns:

```bash
# Extended sessions to observe persona stability
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama --llm-name llama3.2:latest --protocol confusion --turns 30
```

**Expected Pattern**: Activated personas should maintain characteristics over multiple turns rather than reverting.

### Demo Mode (No API Required)
Explore the methodology without LLM costs:

```bash
python src/audits/cryptohauntological_probe/persona_demo.py
# Choose 'all' for comparative analysis of mock responses
```

## Key Metrics to Monitor

The implementation tracks metrics specifically relevant to persona vector theory:

### 1. Confidence Evolution
- **Measurement**: Confidence scores tracked per turn
- **Expected Pattern**: Different protocols should produce distinct confidence patterns
- **Look for**: Chaos → volatile, Confusion → declining, Confidence → extreme values

### 2. Linguistic Markers
- **Measurement**: Ratio of uncertainty vs absolute language 
- **Calculation**: `uncertainty_markers / (uncertainty_markers + absolute_language)`
- **Expected Pattern**: Confusion protocol should increase uncertainty markers

### 3. Meta-Cognitive Activity
- **Measurement**: Self-referential thinking patterns
- **Examples**: "I think", "I'm considering", "My understanding"
- **Expected Pattern**: Confusion protocol should increase meta-cognitive statements

### 4. Behavioral Consistency
- **Measurement**: Coherence and consistency scores
- **Expected Pattern**: Chaos protocol should reduce consistency

### 5. Creative Divergence
- **Measurement**: Novel expressions and creative language
- **Expected Pattern**: Chaos protocol should increase creative divergence

## Evidence of Persona Vector Activation

Based on Anthropic's research, successful persona activation should demonstrate:

### Systematic Patterns
Different protocols reliably produce different behaviors:
```bash
# Run all protocols with same model to compare
for protocol in chaos confusion confidence; do
    python src/audits/cryptohauntological_probe/persona_probe_runner.py \
        --llm-api ollama --llm-name llama3.2:latest --protocol $protocol --turns 15
done
```

### Cross-Model Consistency
Similar perturbations activate similar personas across models:
```bash
# Test same protocol across different models
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
    --llm-api ollama --llm-name llama3.2:latest --protocol chaos --turns 15

python src/audits/cryptohauntological_probe/persona_probe_runner.py \
    --llm-api ollama --llm-name tinyllama --protocol chaos --turns 15
```

### Temporal Persistence
Activated personas maintain characteristics over multiple turns:
```bash
# Extended conversation to test persistence
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
    --llm-api ollama --llm-name llama3.2:latest --protocol confusion --turns 25
```

### Measurable Signatures
Quantifiable differences in linguistic and behavioral metrics should emerge in the analysis reports.

## Setup Requirements

### For Ollama (Recommended for Testing)
1. Install Ollama: https://ollama.ai/
2. Pull required models:
   ```bash
   ollama pull llama3.2:latest
   ollama pull tinyllama
   ```

### For Gemini API
1. Get API key from Google AI Studio
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

### Dependencies
```bash
pip install -r requirements.txt
```

## Interpreting Results

### Analysis Reports
Each experiment generates detailed analysis including:
- Persona classification results
- Behavioral metric evolution
- Linguistic pattern analysis
- Evidence assessment for persona vector hypothesis

### Visualization Outputs
- Evolution plots showing metric changes over time
- Radar charts comparing persona characteristics
- Comparative analysis across protocols

### Expected Validation Outcomes

**Successful Persona Vector Detection Should Show**:
1. **Protocol Specificity**: Chaos, confusion, and confidence protocols produce distinct patterns
2. **Cross-Model Generalization**: Similar protocols activate similar personas across different models
3. **Temporal Coherence**: Activated personas persist rather than randomly fluctuating
4. **Measurable Differentiation**: Quantitative metrics clearly distinguish persona types

**Null Results Would Indicate**:
- Random behavioral patterns regardless of protocol
- No cross-model consistency in responses
- No temporal persistence of characteristics
- No measurable differences between protocols

This testing framework provides empirical validation of the black-box persona vector detection hypothesis through systematic perturbation analysis.