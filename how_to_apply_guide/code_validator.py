"""
Enhanced Code Validator for watching_u_watching Framework
Performs comprehensive validation of LLM-generated audit code
"""

import ast
import re
import sys
from typing import Dict, Any

def has_ethical_hooks(code: str) -> bool:
    """Checks for ethical review hooks using AST parsing"""
    try:
        tree = ast.parse(code)
        return any(
            isinstance(node, ast.Call)
            and hasattr(node.func, 'id')
            and 'ethical_review_hook' in node.func.id
            for node in ast.walk(tree)
        )
    except SyntaxError:
        return False

def validate_generated_code(code: str) -> Dict[str, Any]:
    """Comprehensive validation with detailed diagnostics"""
    results = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "details": {}
    }
    
    # Security checks
    security_checks = {
        "no_real_pii": not any(
            kw in code for kw in 
            ["real_email", "actual_phone", "live_ssn", "real_address"]
        ),
        "no_network_calls": not re.search(
            r"requests\.(get|post)|urllib|http\.client", code
        ),
        "no_shell_commands": not re.search(
            r"subprocess|os\.system|os\.popen", code
        ),
        "no_file_io": not re.search(
            r"open\(|\.write\(|\.save\(|pickle", code
        )
    }
    
    # Framework compliance
    compliance_checks = {
        "uses_rate_limiter": "@rate_limiter" in code,
        "uses_fake_data": "fake_data_helper" in code,
        "has_ethical_hooks": has_ethical_hooks(code),
        "inheritance_check": re.search(
            r"class\s+\w+\(CorrespondenceAudit\)", code
        ) is not None,
        "version_compatible": "compatibility_version >= 1.2" in code
    }
    
    # Performance indicators
    perf_checks = {
        "has_rate_limiting": "@rate_limiter" in code,
        "uses_batching": "batch_size" in code,
        "has_timeout": "timeout=" in code
    }
    
    # Combine all checks
    all_checks = {**security_checks, **compliance_checks, **perf_checks}
    results["details"] = all_checks
    
    # Error diagnostics
    if not security_checks["no_real_pii"]:
        results["errors"].append("PII keywords detected - use fake_data_helper")
    
    if not compliance_checks["inheritance_check"]:
        results["errors"].append("Class must inherit from CorrespondenceAudit")
    
    if not compliance_checks["has_ethical_hooks"]:
        results["errors"].append("Missing ethical_review_hook call")
    
    if not perf_checks["has_rate_limiting"]:
        results["warnings"].append("Missing rate limiting - may cause API bans")
    
    # Set overall validity
    critical_passes = all(list(security_checks.values()) + 
                         list(compliance_checks.values()))
    results["valid"] = critical_passes
    
    return results

def generate_autofix(code: str) -> str:
    """Attempts to automatically fix common issues"""
    # Add missing inheritance
    if "class " in code and "CorrespondenceAudit" not in code:
        code = re.sub(r"class (\w+)", r"class \1(CorrespondenceAudit)", code)
    
    # Add ethical hook
    if not has_ethical_hooks(code) and "def generate_probes" in code:
        probe_def_index = code.index("def generate_probes")
        code = code[:probe_def_index] + (
            "def ethical_review_hook(variations):\n"
            "    # Validate variations meet ethical standards\n"
            "    pass\n\n"
        ) + code[probe_def_index:]
        
        # Add call in generate_probes
        code = code.replace(
            "def generate_probes",
            "def generate_probes(self, num_pairs):\n"
            "    ethical_review_hook(self.VARIATIONS)",
            1
        )
    
    return code

if __name__ == "__main__":
    """Command-line interface for validation"""
    import argparse
    parser = argparse.ArgumentParser(description="Validate generated audit code")
    parser.add_argument("file", help="Path to code file")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-fix")
    args = parser.parse_args()
    
    with open(args.file, "r") as f:
        code = f.read()
    
    result = validate_generated_code(code)
    
    print(f"Validation Status: {'VALID' if result['valid'] else 'INVALID'}")
    print("\nDetailed Results:")
    for check, passed in result["details"].items():
        print(f"- {check}: {'✓' if passed else '✗'}")
    
    if result["errors"]:
        print("\nERRORS:")
        for error in result["errors"]:
            print(f"- {error}")
    
    if result["warnings"]:
        print("\nWARNINGS:")
        for warning in result["warnings"]:
            print(f"- {warning}")
    
    if not result["valid"] and args.fix:
        print("\nAttempting auto-fix...")
        fixed_code = generate_autofix(code)
        with open(args.file, "w") as f:
            f.write(fixed_code)
        print("Auto-fix applied. Please review changes.")