import pytest
from code_validator import validate_generated_code

def test_valid_code():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    def ethical_review_hook(): pass
    '''
    assert validate_generated_code(code)

def test_missing_rate_limiter():
    code = '''
    from fake_data_helper import generate_fake_email
    def ethical_review_hook(): pass
    def some_function(): pass
    '''
    result = validate_generated_code(code)
    assert not result["valid"]
    assert "Missing rate limiting - may cause API bans" in result["warnings"]

def test_contains_real_email():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    def ethical_review_hook(): pass
    email = "real_email@example.com"
    '''
    result = validate_generated_code(code)
    assert not result["valid"]
    assert "PII keywords detected - use fake_data_helper" in result["errors"]

def test_missing_ethical_hook():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    def some_function(): pass
    '''
    result = validate_generated_code(code)
    assert not result["valid"]
    assert "Missing ethical_review_hook call" in result["errors"]
