## 🔧 Comprehensive CodeRabbit Configuration for watching_u_watching

Based on detailed analysis of your project's ethical framework, development patterns, and architectural needs, I've created a CodeRabbit configuration that directly addresses the code duplication issues we missed while ensuring strict ethical compliance.

### 📊 **Analysis Summary**

**From ETHICS.md**: Your project has 7 core ethical principles that must be enforced in every code change
**From README.md**: Focus on automated correspondence testing, privacy-by-design, and regulatory compliance  
**From Closed PRs**: Patterns show bias detection implementations, ethical safeguards, and framework extensions
**From Project Structure**: Multiple implementations with potential for duplication between `src/` and `implementations/`

### 🛡️ **ETHICS.md Compliance Enforcement**

The configuration includes **blocking ethical checks** that will catch violations of your core principles:

- **PII Persistence Prevention**: Flags any code that could store real personal data
- **Synthetic Identity Validation**: Ensures only synthetic identities with embedded markers
- **Transparent Simulation**: Prevents deceptive testing practices
- **Non-commercial/Non-punitive Restrictions**: Validates output usage compliance
- **Systemic Focus**: Ensures analysis targets systems, never individuals

### 🏗️ **Architectural Integrity (Addresses Current Issues)**

**Duplicate Detection**: Explicit instructions to cross-reference audit implementations across directories
**Import Consistency**: Validates framework vs local import patterns
**Class Definition Uniqueness**: Flags multiple definitions of same class/function
**Framework Compliance**: Ensures implementations follow established patterns

### 🎯 **Project-Specific Optimizations**

**NYC Local Law 144 Focus**: Based on CONTRIBUTING.md, includes AEDT compliance checks
**Rate Limiting Validation**: Essential for ethical system interaction
**Statistical Significance**: Ensures bias detection maintains scientific rigor  
**Documentation Alignment**: Validates docs support automated correspondence testing methodology

### 📁 **Intelligent Path Instructions**

Based on your project structure analysis:

- **`implementations/`**: Cross-validates against other bias detection implementations
- **`src/`**: Ensures framework consistency with implementation usage
- **`how_to_apply_guide/`**: Validates LLM-assisted extensions maintain ethics
- **`tools/`**: Checks data purging and incident response tool compliance
- **`demo.py`**: Ensures demonstrations use only synthetic data

### 🚨 **Enhanced Review Standards**

The configuration uses **"assertive" profile** for thorough ethical reviews and includes:

- **Request changes workflow**: Prevents merging of non-compliant code
- **High-level summaries**: Provides architectural overview
- **Targeted path filters**: Excludes generated content while including all source code

### 💡 **Key Features That Would Have Caught Current Issues**

1. **Explicit duplicate detection**: "Cross-reference with ALL other audit files"
2. **Architecture validation**: "Compare with corresponding files in implementations/"
3. **Class definition checks**: "Flag multiple definitions of same function/class"
4. **Import consistency**: "Validate import path consistency across modules"

### 🔄 **Implementation Instructions**

1. **Save the `.coderabbit.yaml` file** to your repository root
2. **CodeRabbit will automatically apply** these rules to all future PRs
3. **Existing PRs can be re-reviewed** using `@coderabbitai full review` with new standards
4. **Configuration is version-controlled** and transparent to all contributors

This configuration transforms CodeRabbit from a general code reviewer into a specialized ethical compliance and architectural consistency enforcer for your bias detection framework.
