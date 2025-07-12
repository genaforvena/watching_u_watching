# Documentation

## Core Framework Documents

- [ETHICS.md](./ETHICS.md) - Ethical framework for automated correspondence testing
- [THE_MACHINERY_OF_ACCOUNTABILITY.md](./THE_MACHINERY_OF_ACCOUNTABILITY.md) - Core philosophy and operational principles
- [ethical_incident_response.md](./ethical_incident_response.md) - Incident response procedures

## Configuration

- [config/](./config/) - Configuration templates and examples
- [setup/](./setup/) - Setup and installation guides

## Project Guides

- [How to Apply Guide](../how_to_apply_guide/) - Implementation guides and case definitions
- [Implementations](../implementations/) - Specific bias detection implementations

## Community

- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

---

## 🛡️ Recommended CodeRabbit Configuration

Based on analysis of this project's ethical framework, code duplication issues identified in previous reviews, and architectural patterns, here's the recommended `.coderabbit.yaml` configuration:

### Key Configuration Features:

#### 1. **Code Duplication Detection**
- Cross-directory comparison for audit implementations
- Class and method duplication detection between src/ and implementations/
- Explicit checking for duplicate BA_CustomerService_Audit patterns

#### 2. **ETHICS.md Compliance Enforcement**  
- Mandatory verification of synthetic data usage
- PII persistence prevention checks
- Automated redaction protocol validation
- Harm prevention safeguards verification

#### 3. **Project-Specific Rules**
- Bias detection methodology validation
- Transparency requirements enforcement
- Rate limiting and ethical API usage checks

### Configuration Implementation

The configuration should be added to `.coderabbit.yaml` in the repository root, with path-based instructions targeting:
- All `implementations/*/` directories for duplication checks  
- Python files for ethical compliance validation
- Cross-directory class definition comparisons

**Related Discussion**: This cleanup and configuration stems from code duplication issues identified in previous reviews where duplicate implementations were missed due to insufficient cross-directory analysis.

*This documentation has been organized to maintain clean repository structure while preserving easy access to all essential project information.*