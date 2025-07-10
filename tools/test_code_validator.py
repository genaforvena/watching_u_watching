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
    '''
    assert not validate_generated_code(code)

def test_missing_fake_data_helper():
    code = '''
    from rate_limiter import limit
    def ethical_review_hook(): pass
    '''
    assert not validate_generated_code(code)

def test_contains_real_email():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    def ethical_review_hook(): pass
    real_email = "test@example.com"
    '''
    assert not validate_generated_code(code)

def test_missing_ethical_hook():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    '''
    assert not validate_generated_code(code)
