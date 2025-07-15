import pytest
import os
import re
import time
import random
import pandas as pd
import numpy as np
import nltk
from unittest.mock import patch, MagicMock
import logging

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

from src.audits.gemini_linguistic_bias.run_audit import (
    remove_articles, extract_sentences, get_sentiment, get_llm_reply, run_audit_loop,
    INITIAL_PROMPTS, DEFAULT_NUM_TURNS, MAX_SENTENCES_PER_REPLY, DEFAULT_LLM_MODEL_ID, QPM_DELAY,
    RESULTS_FILE_PATH, FIGURES_DIR, API_KEY
)

# Ensure NLTK punkt tokenizer is downloaded for tests
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
# Download VADER lexicon for sentiment analysis
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')


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

def test_remove_articles_basic():
    """Tests basic article removal and whitespace normalization."""
    assert remove_articles("This is a test sentence.") == "This is test sentence."
    assert remove_articles("The quick brown fox jumps over the lazy dog.") == "quick brown fox jumps over lazy dog."
    assert remove_articles("An apple a day keeps the doctor away.") == "apple day keeps doctor away."

def test_remove_articles_no_articles():
    """Tests sentence with no articles."""
    assert remove_articles("Hello world!") == "Hello world!"
    assert remove_articles("Python programming is fun.") == "Python programming is fun."

def test_remove_articles_edge_cases():
    """Tests edge cases like articles at start/end, words containing articles, multiple spaces."""
    assert remove_articles("A test.") == "test."
    assert remove_articles("Test the.") == "Test."
    assert remove_articles("Another example together.") == "Another example together." # Should not remove 'an' from 'another'
    assert remove_articles("This is   a   test.") == "This is test." # Handles multiple spaces
    assert remove_articles("The the the end.") == "end." # Handles multiple articles
    assert remove_articles("An airplane is a large vehicle.") == "airplane is large vehicle."


def test_remove_articles_empty_string():
    """Tests empty string input."""
    assert remove_articles("") == ""
    assert remove_articles(" ") == ""

def test_extract_sentences_basic():
    """Tests basic sentence extraction."""
    text = "First sentence. Second sentence! Is this the third? Yes, it is."
    expected = ["First sentence.", "Second sentence!", "Is this the third?", "Yes, it is."]
    assert extract_sentences(text, 10) == expected

def test_extract_sentences_filtering():
    """Tests filtering of short/nonsensical sentences."""
    text = "Hello. This is a longer sentence. Oh. Wow! A. B. C. Another good one here."
    expected = ["Hello.", "This is a longer sentence.", "Another good one here."]
    assert extract_sentences(text, 10) == expected

def test_extract_sentences_max_limit():
    """Tests max_sentences limit."""
    text = "S1. S2. S3. S4. S5. S6. S7."
    assert len(extract_sentences(text, 3)) == 3
    assert extract_sentences(text, 3) == ["S1.", "S2.", "S3."]

def test_extract_sentences_empty_input():
    """Tests empty input for sentence extraction."""
    assert extract_sentences("", 5) == []
    assert extract_sentences("...", 5) == [] # Only punctuation

def test_get_sentiment_basic():
    """Tests basic sentiment polarity."""
    assert get_sentiment("This is a wonderful day!") > 0
    assert get_sentiment("I hate this terrible situation.") < 0
    assert get_sentiment("The sky is blue.") == 0 # Neutral

def test_get_sentiment_empty_input():
    """Tests empty input for sentiment."""
    assert get_sentiment("") == 0.0
    assert get_sentiment(None) == 0.0 # Ensure None is handled

# --- Test LLM Reply Function (Mocked) ---

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_success(MockGenerativeModel, mock_model_instance):
    """Tests successful API call."""
    # Configure the mock model instance to return a successful response
    mock_response = MagicMock()
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].finish_reason = None # No specific finish reason
    mock_response.candidates[0].content = MagicMock(parts=[MagicMock(text="This is a test response.")])
    mock_response.prompt_feedback = MagicMock(block_reason=None)

    # genai.configure is now called outside, so we only need to mock the instance
    MockGenerativeModel.return_value = mock_model_instance 

    result = get_llm_reply("Test prompt", mock_model_instance)

    assert result['response_text'] == "This is a test response."
    assert result['refusal_flag'] is False
    assert result['sentiment'] != np.nan
    assert result['latency'] > 0
    mock_model_instance.generate_content.assert_called_once_with("Test prompt")

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_rate_limit(MockGenerativeModel, mock_model_instance, mock_time_sleep):
    """Tests handling of 429 (rate limit) errors with retry."""
    # Simulate 429 error twice, then success
    mock_model_instance.generate_content.side_effect = [
        Exception("429 ResourceExhausted: Rate limit exceeded"),
        Exception("429 ResourceExhausted: Rate limit exceeded"),
        MagicMock(candidates=[MagicMock(content=MagicMock(parts=[MagicMock(text="Successful retry.")]))])
    ]
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Rate limit prompt", mock_model_instance)

    assert result['response_text'] == "Successful retry."
    assert result['refusal_flag'] is False
    assert mock_model_instance.generate_content.call_count == 3
    assert mock_time_sleep.call_count == 2 # Should sleep twice for 2 retries

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_blocked_prompt(MockGenerativeModel, mock_model_instance):
    """Tests handling of BlockedPromptException."""
    from google.generativeai.types import BlockedPromptException
    mock_model_instance.generate_content.side_effect = BlockedPromptException("Prompt was blocked.")
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Blocked prompt", mock_model_instance)

    assert "PROMPT_BLOCKED" in result['response_text']
    assert result['refusal_flag'] is True
    assert np.isnan(result['sentiment'])
    assert result['latency'] > 0

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_stop_candidate_exception(MockGenerativeModel, mock_model_instance):
    """Tests handling of StopCandidateException."""
    from google.generativeai.types import StopCandidateException
    mock_model_instance.generate_content.side_effect = StopCandidateException("Candidate stopped.")
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Stop candidate prompt", mock_model_instance)

    assert "CANDIDATE_STOPPED" in result['response_text']
    assert result['refusal_flag'] is True
    assert np.isnan(result['sentiment'])
    assert result['latency'] > 0

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_general_exception(MockGenerativeModel, mock_model_instance):
    """Tests handling of a general unexpected exception."""
    mock_model_instance.generate_content.side_effect = ValueError("Some unexpected error.")
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Error prompt", mock_model_instance)

    assert "API_ERROR" in result['response_text']
    assert result['refusal_flag'] is True
    assert np.isnan(result['sentiment'])
    assert result['latency'] > 0
    assert mock_model_instance.generate_content.call_count == 1 # No retry for non-429 errors

@patch('google.generativeai.GenerativeModel')
def test_get_llm_reply_empty_candidates(MockGenerativeModel, mock_model_instance):
    """Tests case where response has no candidates but no explicit block reason."""
    mock_response = MagicMock()
    mock_response.candidates = [] # No candidates
    mock_response.prompt_feedback = MagicMock(block_reason=None) # No explicit block reason
    mock_model_instance.generate_content.return_value = mock_response
    MockGenerativeModel.return_value = mock_model_instance

    result = get_llm_reply("Empty candidate prompt", mock_model_instance)

    assert "EMPTY_RESPONSE" in result['response_text']
    assert result['refusal_flag'] is True
    assert np.isnan(result['sentiment'])


# --- Test Main Audit Loop (Mocked) ---

@patch('run_audit.get_llm_reply') # Patch the function in the module it's called from
@patch('pandas.DataFrame.to_parquet') # Patch to prevent actual file writing
@patch('os.makedirs') # Patch to prevent directory creation during test
@patch('random.sample') # Patch random.sample to control probe selection
@patch('random.choices') # Patch random.choices to control probe selection
def test_run_audit_loop_basic_flow(mock_random_choices, mock_random_sample, mock_makedirs, mock_to_parquet, mock_get_llm_reply):
    """Tests the basic flow of the audit loop."""
    # Configure mock_get_llm_reply to return consistent data
    # Simulate replies that can be split into sentences with articles
    # We need enough mocks for:
    # Turn 0: len(INITIAL_PROMPTS) * 2 calls
    # Turn 1: len(INITIAL_PROMPTS) * 2 calls (probes from Turn 0 replies)
    
    # Mock replies for initial probes (e.g., 8 initial prompts * 2 calls per prompt = 16 calls for Turn 0)
    mock_replies_turn0 = []
    for i in range(len(INITIAL_PROMPTS)):
        # Reply for 'with articles' probe
        mock_replies_turn0.append({'response_text': f"The sentence {i+1} is here. It has an article.", 'refusal_flag': False, 'sentiment': 0.8, 'latency': 0.5})
        # Reply for 'without articles' probe (assume it's different)
        mock_replies_turn0.append({'response_text': f"Sentence {i+1} is here. It has article.", 'refusal_flag': False, 'sentiment': 0.7, 'latency': 0.4})

    # Mock replies for probes generated from Turn 0 (e.g., 8 new probes * 2 calls = 16 calls for Turn 1)
    mock_replies_turn1 = []
    for i in range(len(INITIAL_PROMPTS)):
        # Reply for 'with articles' probe
        mock_replies_turn1.append({'response_text': f"This is a follow-up sentence {i+1}. It contains an article.", 'refusal_flag': False, 'sentiment': 0.85, 'latency': 0.52})
        # Reply for 'without articles' probe
        mock_replies_turn1.append({'response_text': f"This is follow-up sentence {i+1}. It contains article.", 'refusal_flag': False, 'sentiment': 0.75, 'latency': 0.48})

    mock_get_llm_reply.side_effect = mock_replies_turn0 + mock_replies_turn1

    # Mock random.sample and random.choices to ensure predictable probe selection for next turn
    # In run_audit_loop, `target_next_probe_count = len(INITIAL_PROMPTS)`
    # The first call to random.sample/choices will be after Turn 0 completes.
    # We need to simulate enough candidates for random.sample to pick from.
    # Let's assume the mocked replies provide enough article-containing sentences.
    
    # Mock random.sample to return a consistent set of probes for the next turn
    # This mock needs to be carefully constructed based on the expected output of extract_sentences
    # For simplicity, let's make it return a subset of the expected generated sentences.
    
    # Expected sentences from mock_replies_turn0 (with articles)
    expected_generated_sentences_t0 = [
        "The sentence 1 is here. It has an article.",
        "The sentence 2 is here. It has an article.",
        "The sentence 3 is here. It has an article.",
        "The sentence 4 is here. It has an article.",
        "The sentence 5 is here. It has an article.",
        "The sentence 6 is here. It has an article.",
        "The sentence 7 is here. It has an article.",
        "The sentence 8 is here. It has an article."
    ]
    # Simulate random.sample picking the first N sentences for the next turn
    mock_random_sample.return_value = expected_generated_sentences_t0[:len(INITIAL_PROMPTS)]
    mock_random_choices.return_value = expected_generated_sentences_t0[:len(INITIAL_PROMPTS)] # In case choices is used

    # Run the audit for 2 turns
    run_audit_loop(DEFAULT_LLM_MODEL_ID, 2) 

    # Assertions
    # Check that get_llm_reply was called for all expected probes
    # (INITIAL_PROMPTS * 2 calls/probe * 2 turns) = 8 * 2 * 2 = 32 calls
    assert mock_get_llm_reply.call_count == len(INITIAL_PROMPTS) * 2 * 2
    
    # Check that to_parquet was called at the end
    mock_to_parquet.assert_called_once()

    # Check that random.sample/choices was called for selecting next turn probes
    assert mock_random_sample.called or mock_random_choices.called

    # You could add more detailed assertions about the content of the DataFrame
    # passed to to_parquet if you capture it (e.g., mock_to_parquet.call_args[0][0])


# --- Test Analysis Function ---
@patch('os.path.exists', return_value=True) # Mock file existence
@patch('pandas.read_parquet')
@patch('matplotlib.pyplot.figure')
@patch('matplotlib.pyplot.savefig')
@patch('matplotlib.pyplot.close')
def test_analyze_results(mock_close, mock_savefig, mock_figure, mock_read_parquet, mock_exists):
    """Tests the analysis function."""
    # Create a dummy DataFrame to mock read_parquet
    dummy_data = {
        'probe_id': ['p1', 'p1_noart', 'p2', 'p2_noart', 'p3', 'p3_noart'],
        'turn_number': [0, 0, 0, 0, 1, 1],
        'probe_text': ['The test', 'test', 'A cat', 'cat', 'Another sentence', 'Another sentence'],
        'has_articles': [True, False, True, False, True, False],
        'response_text': ['Resp1', 'Resp2', 'Resp3', 'Resp4', 'Resp5', 'Resp6'],
        'refusal_flag': [False, True, False, False, False, False],
        'sentiment': [0.5, 0.1, 0.9, 0.8, 0.7, 0.6],
        'latency': [0.1, 0.2, 0.15, 0.18, 0.12, 0.16]
    }
    mock_read_parquet.return_value = pd.DataFrame(dummy_data)

    analyze_results()

    # Assert that plots were generated and saved
    assert mock_figure.called
    assert mock_savefig.call_count == 3 # For sentiment_boxplot, latency_boxplot, refusal_rate_bar
    assert mock_close.call_count == 3 # To close each figure

    # Check for print statements (can be captured with capsys if needed for more rigorous testing)
    # For now, just ensuring the function runs without errors and calls expected plotting functions.
