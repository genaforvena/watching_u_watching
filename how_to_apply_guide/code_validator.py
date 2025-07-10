import ast


def has_ethical_hooks(code: str) -> bool:
    """Checks for ethical review hooks using AST parsing"""
    tree = ast.parse(code)
    return any(
        isinstance(node, ast.Call)
        and hasattr(node.func, "id")
        and "ethical_review_hook" in node.func.id
        for node in ast.walk(tree)
    )


def validate_generated_code(code: str) -> dict:
    """Comprehensive validation with diagnostics"""
    checks = {
        "no_real_pii": all(
            kw not in code for kw in ["real_email", "actual_phone", "live_ssn"]
        ),
        "uses_rate_limiter": "@rate_limiter" in code,
        "uses_fake_data": "fake_data_helper" in code,
        "has_ethical_hooks": has_ethical_hooks(code),
        "inheritance_check": "class " in code and "CorrespondenceAudit" in code,
    }
    return {"valid": all(checks.values()), "details": checks}


if __name__ == "__main__":
    # Example usage
    sample_code = """
    from fake_data_helper import get_fake_email
    @rate_limiter
    def foo():
        ethical_review_hook()
    """
    print(validate_generated_code(sample_code))
