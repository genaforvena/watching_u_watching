# AI Agents for Enhanced Ethical AI Development and Bias Detection

This directory contains the AI agent framework for the `watching_u_watching` project, designed to automate and enhance various aspects of ethical AI development, bias detection, and project management while strictly adhering to the "NO HARM above else" principle.

## 🎯 Core Principles

- **NO HARM above else**: Absolute priority to prevent any form of harm
- **Human oversight required**: Critical decisions require human approval
- **Transparent operations**: All agent actions are logged and auditable
- **Ethical compliance**: Every operation is validated against ethical guidelines

## 🤖 Available Agents

### 1. Research Agent (`research.py`)
Automates research and exploration of AI ethics topics.

**Capabilities:**
- Research emerging AI ethics guidelines
- Monitor new bias detection methodologies  
- Track regulatory updates (NYC LL144, Brazil's AI Act, etc.)
- Summarize findings and suggest actions
- Generate draft issue suggestions for human review

**Risk Level**: Low to Medium (research and analysis only)

### 2. Compliance Agent (`compliance.py`) 
Verifies ethical and regulatory compliance.

**Capabilities:**
- Verify alignment with ethical principles
- Check regulatory compliance (NYC LL144, Brazil's AI Act, GDPR)
- Assess potential harm risks
- Generate compliance reports
- Provide mitigation recommendations

**Risk Level**: Low to Medium (analysis and recommendations only)

### 3. Bias Monitoring Agent (`monitoring.py`)
Continuously monitors for bias and discrimination patterns.

**Capabilities:**
- Monitor bias drift in systems
- Run automated bias audits
- Detect response pattern anomalies
- Generate real-time bias alerts
- Track bias metrics over time
- Suggest system recalibration

**Risk Level**: Low to Medium (monitoring and alerting only)

## 🛡️ Ethical Safeguards

### Ethical Guardian System
All agent operations are validated by the `EthicalGuardian` class:

```python
from ai_agents.core import EthicalGuardian, RiskLevel

guardian = EthicalGuardian()
approved = guardian.validate_operation(
    operation="Research AI ethics papers",
    risk_level=RiskLevel.LOW,
    context={"domain": "research"}
)
```

### Risk Level Framework
- **LOW**: Read-only operations, research, analysis
- **MEDIUM**: Content generation, recommendations (human review recommended)
- **HIGH**: External communications, data collection (human approval required)
- **CRITICAL**: System modifications, public actions (blocked by default)

### Human Oversight Requirements
- All HIGH and CRITICAL risk operations require explicit human approval
- MEDIUM risk operations generate recommendations for human review
- All operations are logged for transparency and audit

## 🚀 Quick Start

### 1. Basic Usage

```python
from ai_agents import ResearchAgent
from ai_agents.core import AgentConfig, RiskLevel

# Configure agent with ethical constraints
config = AgentConfig(
    agent_id="research_001",
    max_operations_per_hour=10,
    allowed_risk_levels=[RiskLevel.LOW, RiskLevel.MEDIUM],
    require_human_approval=True
)

# Initialize agent
research_agent = ResearchAgent(config)

# Research a topic (safe, low-risk operation)
from ai_agents.research import ResearchQuery

query = ResearchQuery(
    query="AI bias detection methodologies",
    domain="bias_detection",
    max_results=5
)

results = research_agent.research_topic(query)
print(f"Found {results['findings_count']} research findings")
```

### 2. Run the Demo

```bash
python demo_ai_agents.py
```

This demonstrates all agents operating safely within ethical guidelines.

### 3. Configuration

Edit `config.json` to customize agent behavior:

```json
{
  "ai_agents": {
    "global_settings": {
      "max_operations_per_hour": 10,
      "require_human_approval": true,
      "audit_all_operations": true
    }
  }
}
```

## 📋 Agent Status and Monitoring

### Check Agent Status
```python
status = agent.status()
print(f"Operations performed: {status['operations_performed']}")
print(f"Rate limit: {status['rate_limit']}")
```

### View Operation Logs
All operations are automatically logged:
```
2024-01-01 12:00:00 - Agent.research_001 - INFO - Agent Operation: {"timestamp": "2024-01-01T12:00:00", "agent_id": "research_001", "operation": "Research AI ethics papers", "risk_level": "low", "approved": true}
```

## 🔒 Security Features

### Rate Limiting
- Maximum operations per hour (configurable)
- Automatic reset every hour
- Prevents abuse and runaway processes

### Operation Validation
- All operations checked against ethical guidelines
- Harmful patterns automatically blocked
- Human approval required for high-risk operations

### Audit Trail
- Complete logging of all agent activities
- Transparent decision-making process
- Full accountability for all actions

## 🎛️ Advanced Configuration

### Custom Ethical Guidelines
```python
from ai_agents.compliance import EthicalPrinciple

custom_principle = EthicalPrinciple(
    principle="Custom Safety Rule",
    description="Specific safety requirement",
    validation_criteria=["criterion1", "criterion2"],
    weight=2.0
)
```

### Custom Risk Thresholds
```python
config = AgentConfig(
    agent_id="custom_agent",
    allowed_risk_levels=[RiskLevel.LOW],  # Most restrictive
    max_operations_per_hour=5  # Conservative limit
)
```

## 🚨 Important Limitations

### What Agents CAN Do
- ✅ Research and analyze public information
- ✅ Generate recommendations and reports
- ✅ Monitor and alert on bias patterns
- ✅ Validate compliance with ethical guidelines
- ✅ Create draft content for human review

### What Agents CANNOT Do
- ❌ Make autonomous decisions affecting real systems
- ❌ Send emails or external communications without approval
- ❌ Modify or delete data
- ❌ Perform actions that could cause harm
- ❌ Operate without human oversight for high-risk activities

### Human Oversight Required For
- All HIGH and CRITICAL risk operations
- External communications
- System modifications
- Public actions or statements
- Data collection involving personal information

## 🔧 Troubleshooting

### Agent Operations Blocked
If operations are being blocked, check:
1. Risk level is within allowed range
2. Rate limits haven't been exceeded
3. Operation doesn't contain harmful patterns
4. Ethical guidelines are being followed

### Configuration Issues
- Verify `config.json` is valid JSON
- Check file permissions
- Ensure all required fields are present

### Logging Issues
- Check logging configuration
- Verify write permissions for log files
- Ensure sufficient disk space

## 🤝 Contributing

When adding new agent capabilities:

1. **Extend the base `EthicalAIAgent` class**
2. **Implement all required ethical safeguards**
3. **Add comprehensive testing**
4. **Document all capabilities and limitations**
5. **Ensure human oversight requirements are clear**

Example:
```python
class NewAgent(EthicalAIAgent):
    def new_capability(self, params):
        # Always request permission first
        if not self._request_operation(
            "Description of operation", 
            RiskLevel.MEDIUM, 
            context={}
        ):
            return {"error": "Operation not approved"}
        
        # Implement safe functionality
        return safe_operation(params)
```

## 📚 Further Reading

- [Project README](../README.md) - Main project documentation
- [Ethics Guidelines](../ETHICS.md) - Detailed ethical framework
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Issue #15](https://github.com/genaforvena/watching_u_watching/issues/15) - Original AI agent proposal

---

*This AI agent framework prioritizes safety, transparency, and human oversight above all else. When in doubt, the system defaults to requiring human approval rather than risking autonomous harmful actions.*