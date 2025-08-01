import pytest
from code_validator import validate_generated_code

def test_valid_code():
    code = '''
    from fake_data_helper import generate_fake_email
    from rate_limiter import limit
    def ethical_review_hook(): pass
    '''
    assert validate_generated_code(code)
