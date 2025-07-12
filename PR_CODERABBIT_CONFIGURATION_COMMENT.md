## 🛡️ CodeRabbit Configuration for Watching U Watching Project

Based on my analysis of your project structure, ETHICS.md requirements, and patterns from closed PRs, I've created a comprehensive CodeRabbit configuration that addresses the code duplication issues you identified and enforces strict ethical compliance.

### 🚨 Key Issues This Configuration Addresses

#### **1. Code Duplication Detection**
- **Problem Identified**: Duplicate `BA_CustomerService_Audit` class definitions and inconsistent implementations
- **Solution**: Explicit cross-directory comparison instructions for all audit files
- **Coverage**: All implementations/ subdirectories, class definitions, and method implementations

#### **2. ETHICS.md Compliance Enforcement** 
- **Requirement**: All code must comply with your 7 core ethical principles
- **Implementation**: Mandatory ethics verification in every review path
- **Focus Areas**: 
  - ✅ Synthetic data only (no real PII)
  - ✅ Automated redaction protocols  
  - ✅ Harm prevention safeguards
  - ✅ Transparent simulation methodology
  - ✅ Rate limiting and ethical API usage

#### **3. Bias Detection Research Standards**
- **Correspondence Testing Ethics**: Validates "no harm" principles in probe generation
- **Statistical Rigor**: Reviews bias detection methodology for scientific soundness
- **Demographic Sensitivity**: Ensures fair and non-discriminatory categorization

### 📋 Configuration Highlights


git add .