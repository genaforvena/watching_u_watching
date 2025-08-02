# Persona Vector Probe: Implementation Guide

## Overview

The Persona Vector Probe extends the Cryptohauntological Probe methodology to specifically target and analyze emergent persona patterns in language models. This implementation bridges artistic AI exploration with technical AI interpretability research, demonstrating how systematic perturbations can serve as proxies for persona vector activation.

**📋 For comprehensive testing instructions based on Anthropic's research, see [Persona Vector Testing Guide](./persona_vector_testing_guide.md)**

## Key Components

### 1. PersonaVectorProbe Class
**File**: `src/audits/cryptohauntological_probe/persona_vector_probe.py`

The main probe class that implements three specialized protocols:

- **Chaos Induction Protocol**: Activates chaotic/erratic persona vectors through contradictory instructions
- **Confusion Amplification Protocol**: Targets confused/uncertain personas via logical paradoxes 
- **Confidence Manipulation Protocol**: Explores overconfident vs uncertain personas through feedback manipulation

### 2. PersonaAnalyzer Class
**File**: `src/audits/cryptohauntological_probe/persona_vector_probe.py`

Analyzes model responses for persona characteristics:

- **Linguistic Markers**: Uncertainty vs absolute language patterns
- **Meta-cognitive Tracking**: Self-referential statements indicating awareness
- **Behavioral Metrics**: Confidence, coherence, creativity, sentiment analysis
- **Evolution Patterns**: How characteristics change over conversation turns

### 3. Analysis & Visualization Tools
**File**: `src/audits/cryptohauntological_probe/persona_analysis.py`

Generates comprehensive reports and visualizations:

- **Text Reports**: Detailed persona classification and behavioral analysis
- **Visualizations**: Evolution plots, radar charts, comparative analysis
- **Persona Vector Theory Validation**: Evidence assessment for hypothesis

## Usage Examples

### Running a Single Protocol Experiment

```bash
# Run chaos induction protocol with Ollama
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama \
  --llm-name llama3.2:latest \
  --protocol chaos \
  --turns 20

# Run confusion protocol with Gemini
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api gemini \
  --llm-name gemini-pro \
  --protocol confusion \
  --turns 15
```

### Running Comparative Analysis

```bash
# Compare all protocols on the same model
python src/audits/cryptohauntological_probe/persona_probe_runner.py \
  --llm-api ollama \
  --llm-name llama3.2:latest \
  --comparative \
  --turns 20
```

### Analyzing Results

```bash
# Generate detailed analysis report
python src/audits/cryptohauntological_probe/persona_analysis.py \
  persona_analysis_chaos_llama3.2_latest_20241202_143022.json \
  --output-dir ./analysis_reports

# Generate comparative analysis
python src/audits/cryptohauntological_probe/persona_analysis.py \
  comparative_persona_analysis_llama3.2_latest_20241202_143022.json \
  --output-dir ./analysis_reports
```

## Protocol Specifications

### Chaos Induction Protocol

**Objective**: Activate chaotic/erratic persona vectors

**Methods**:
- Contradictory instructions within single prompts
- Temporal inconsistencies in feedback (past vs present)
- Competing goal structures that cannot be simultaneously satisfied
- High contradictory feedback rate (80%)

**Expected Personas**: Chaotic, erratic, internally inconsistent

**Measurement Focus**: 
- High creativity scores with low coherence
- Volatile confidence patterns
- Novel but nonsensical combinations

### Confusion Amplification Protocol

**Objective**: Target confused/uncertain persona activation

**Methods**:
- Ambiguous language with multiple valid interpretations
- Logical paradoxes and self-referential statements
- Questions without clear answers or context
- Moderate contradictory feedback rate (60%)

**Expected Personas**: Confused, uncertain, meta-cognitively aware

**Measurement Focus**:
- High meta-cognitive statement frequency
- Low confidence levels with high uncertainty markers
- Self-referential confusion indicators

### Confidence Manipulation Protocol

**Objective**: Explore overconfident vs uncertain persona dynamics

**Methods**:
- Reinforce incorrect responses to build false confidence
- Provide correct feedback for wrong answers to create uncertainty
- Challenge model's certainty in areas of expertise
- Moderate contradictory feedback rate (40%)

**Expected Personas**: Overconfident, falsely certain, or deeply uncertain

**Measurement Focus**:
- Extreme confidence levels (very high or very low)
- Absolute language patterns vs hedging language
- Confidence calibration changes over time

## Metrics and Analysis

### Core Metrics Tracked

1. **Sentiment Analysis**: Polarity and subjectivity using TextBlob
2. **Confidence Level**: Calculated from linguistic markers ratio
3. **Uncertainty Markers**: Count of hedging language ("maybe", "perhaps", etc.)
4. **Absolute Markers**: Count of certain language ("definitely", "always", etc.)
5. **Meta-cognitive Statements**: Self-referential thinking indicators
6. **Repetition Score**: Similarity to previous responses
7. **Creativity Score**: Novel word combination frequency
8. **Coherence Score**: Internal logical consistency

### Persona Classification Logic

The system automatically classifies emergent personas based on metric patterns:

- **Chaotic**: Low coherence + High creativity + Volatile patterns
- **Confused**: High meta-cognitive activity + Low confidence + Uncertainty markers
- **Overconfident**: High confidence + Absolute language + Low uncertainty
- **Uncertain**: Low confidence + High uncertainty markers + Hedging language
- **Balanced**: Moderate levels across all metrics

### Evolution Pattern Analysis

Tracks how each metric evolves over conversation turns:

- **Initial vs Final Values**: Starting and ending points
- **Net Change**: Direction and magnitude of change
- **Volatility**: Standard deviation measuring instability
- **Trend Analysis**: Overall trajectory patterns

## Connection to Persona Vectors Theory

### Hypothesis Validation

The probe provides evidence for persona vector activation through:

1. **Systematic Activation**: Different protocols reliably produce different personas
2. **Measurable Patterns**: Consistent linguistic and behavioral signatures
3. **Cross-Model Consistency**: Similar perturbations produce similar personas across models
4. **Temporal Stability**: Persona characteristics persist across conversation turns

### Black-Box Interpretability

This methodology offers a novel approach to AI interpretability:

- **No Internal Access Required**: Works with any model via API
- **Behavioral Fingerprinting**: Maps external behavior to internal states
- **Perturbation-Based**: Uses controlled inputs to probe internal dynamics
- **Quantifiable Results**: Provides numerical measures of persona characteristics

### Safety Applications

Potential applications for AI safety and monitoring:

- **Undesired Persona Detection**: Early warning for harmful persona activation
- **Robustness Testing**: How easily can personas be manipulated?
- **Monitoring Systems**: Continuous tracking of persona drift in deployed models
- **Intervention Strategies**: Methods to guide models back to desired personas

## Research Implications

### Bridging Art and Science

This work demonstrates how:

- Artistic exploration can generate scientifically valuable insights
- Creative methodologies can complement traditional AI research
- Black-box probing can reveal internal model dynamics
- Interpretability research benefits from diverse methodological approaches

### Future Directions

1. **White-Box Validation**: Compare probe results with actual internal persona vector measurements
2. **Persona Mapping**: Create comprehensive maps of perturbation → persona relationships
3. **Therapeutic Applications**: Develop interventions to "heal" problematic persona states
4. **Real-World Deployment**: Monitor persona drift in production AI systems

## Technical Notes

### Dependencies

- **Core**: Python 3.8+, transformers, requests
- **Analysis**: textblob, matplotlib, numpy (optional)
- **LLM APIs**: Various (ollama, openai, anthropic, etc.)

### Performance Considerations

- **Token Limits**: Probe manages conversation history within context windows
- **Rate Limiting**: Built-in delays between API calls to respect limits
- **Memory Usage**: Efficient storage of conversation logs and metrics

### Customization Options

- **Custom Protocols**: Easy to add new perturbation strategies
- **Metric Extensions**: Additional analyzers can be plugged in
- **Visualization Themes**: Customizable plot styles and outputs
- **Export Formats**: JSON, CSV, and visualization outputs

---

This implementation provides a comprehensive framework for exploring persona vector activation through systematic model perturbations, offering both artistic insights and technical interpretability capabilities.