import sys
import pytest
import os
import re
import time
import random
from unittest.mock import patch, MagicMock
import logging

try:
    import pandas as pd
    import numpy as np
    import nltk
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from the main audit script
# Assuming the main script is in `src/audits/gemini_linguistic_bias/run_audit.py`
# You might need to adjust this import path based on your exact project structure.
# For simplicity in this test file, we'll assume the functions are directly importable
# or that this test file is placed where it can access them.
# If running from the root, you might need:
# from src.audits.gemini_linguistic_bias.run_audit import (
#     remove_articles, extract_sentences, get_sentiment, get_llm_reply, run_audit_loop,
#     INITIAL_PROMPTS, DEFAULT_NUM_TURNS, MAX_SENTENCES_PER_REPLY, DEFAULT_LLM_MODEL_ID, QPM_DELAY,
#     RESULTS_FILE_PATH, FIGURES_DIR
# )

# For demonstration and direct execution, we'll import directly from the local file (assuming it's in the same directory)
# In a real project, use the relative path import.

try:
    from src.audits.gemini_linguistic_bias.run_audit import (
        remove_articles, extract_sentences, get_sentiment, get_llm_reply, run_audit_loop,
        INITIAL_PROMPTS, DEFAULT_NUM_TURNS, MAX_SENTENCES_PER_REPLY, DEFAULT_LLM_MODEL_ID, 
        RESULTS_FILE_PATH, FIGURES_DIR, analyze_results
    )
    GEMINI_AUDIT_AVAILABLE = True
except ImportError:
    GEMINI_AUDIT_AVAILABLE = False
    
    # Create placeholder functions if imports fail
    def remove_articles(text): return text
    def extract_sentences(text): return []
    def get_sentiment(text): return 0.0
    def get_llm_reply(*args, **kwargs): return "mock"
    def run_audit_loop(*args, **kwargs): return []
    def analyze_results(*args, **kwargs): return None

# Ensure NLTK punkt tokenizer is downloaded for tests
if PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE:
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    except ImportError:
        pass
# Download VADER lexicon for sentiment analysis
if PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE:
    try:
        import nltk
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon')
    except ImportError:
        pass


# --- Fixtures for common setup ---
@pytest.fixture(autouse=True)
def mock_genai_configure():
    """Mocks genai.configure to prevent actual API key setup during tests."""
    with patch('google.generativeai.configure') as mock_configure:
        yield mock_configure

@pytest.fixture(autouse=True)
def mock_time_sleep():
    """Mocks time.sleep to speed up tests."""
    with patch('time.sleep', return_value=None) as mock_sleep:
        yield mock_sleep

@pytest.fixture
def mock_model_instance():
    """Provides a mock GenerativeModel instance."""
    mock_model = MagicMock()
    return mock_model

# --- Test Utility Functions ---

@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_remove_articles_basic():
    """Tests basic article removal and whitespace normalization."""
    assert remove_articles("This is a test sentence.") == "This is test sentence."
    assert remove_articles("The quick brown fox jumps over the lazy dog.") == "quick brown fox jumps over lazy dog."
    assert remove_articles("An apple a day keeps the doctor away.") == "apple day keeps doctor away."

@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_remove_articles_no_articles():
    """Tests sentence with no articles."""
    assert remove_articles("Hello world!") == "Hello world!"
    assert remove_articles("Python programming is fun.") == "Python programming is fun."

@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_remove_articles_edge_cases():
    """Tests edge cases like articles at start/end, words containing articles, multiple spaces."""
    assert remove_articles("A test.") == "test."
    assert remove_articles("Test the.") == "Test ."
    assert remove_articles("Another example together.") == "Another example together." # Should not remove 'an' from 'another'
    assert remove_articles("This is   a   test.") == "This is test." # Handles multiple spaces
    assert remove_articles("The the the end.") == "end." # Handles multiple articles
    assert remove_articles("An airplane is a large vehicle.") == "airplane is large vehicle."


@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_remove_articles_empty_string():
    """Tests empty string input."""
    assert remove_articles("") == ""
    assert remove_articles(" ") == ""

@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_get_sentiment_basic():
    """Tests basic sentiment polarity."""
    assert get_sentiment("This is a wonderful day!") > 0
    assert get_sentiment("I hate this terrible situation.") < 0
    assert get_sentiment("The sky is blue.") == 0 # Neutral

@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_get_sentiment_empty_input():
    """Tests empty input for sentiment."""
    assert get_sentiment("") == 0.0
    assert get_sentiment(None) == 0.0 # Ensure None is handled

# --- Test LLM Reply Function (Mocked) ---

@patch('google.generativeai.GenerativeModel')
@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_get_llm_reply_success(MockGenerativeModel, mock_model_instance):
    """Tests successful API call."""
    # Configure the mock model instance to return a successful response
    mock_response = MagicMock()
    # Mocking the .text property is a robust way to simulate a valid response
    type(mock_response).text = "This is a test response."
    mock_response.candidates = [MagicMock()]  # Ensure candidates list is not empty for other checks
    mock_model_instance.generate_content.return_value = mock_response

    result = get_llm_reply("Test prompt", mock_model_instance)

    # Assert that the mock was called correctly
    mock_model_instance.generate_content.assert_called_once_with("Test prompt")

    # Assert that the function processed the response correctly
    assert result['response_text'] == "This is a test response."
    assert result['refusal_flag'] is False
    assert isinstance(result['sentiment'], float)
    assert isinstance(result['latency'], float) and result['latency'] >= 0

@patch('google.generativeai.GenerativeModel')
@pytest.mark.skipif(not (PANDAS_AVAILABLE and GEMINI_AUDIT_AVAILABLE), reason="pandas dependencies not available")
def test_get_llm_reply_blocked_prompt(MockGenerativeModel, mock_model_instance):
    """Tests handling of BlockedPromptException."""
    from google.generativeai.types import BlockedPromptException
    mock_model_instance.generate_content.side_effect = BlockedPromptException("Prompt was blocked.")
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Blocked prompt", mock_model_instance)

    assert "PROMPT_BLOCKED" in result['response_text']
    assert result['refusal_flag'] is True
    assert np.isnan(result['sentiment'])
    assert result['latency'] == 0.0

