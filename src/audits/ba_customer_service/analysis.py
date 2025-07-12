import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize NLTK VADER sentiment analyzer
try:
    sid = SentimentIntensityAnalyzer()
except LookupError:
    logging.warning("NLTK vader_lexicon not found. Downloading...")
    # import nltk  # Used for downloading the vader_lexicon
    from nltk import download
    download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()

# TODO: For large-scale audits, consider using a more efficient sentiment analysis library or pre-trained model.
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize NLTK VADER sentiment analyzer
try:
    sid = SentimentIntensityAnalyzer()
except LookupError:
    logging.warning("NLTK vader_lexicon not found. Downloading...")
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()

# TODO: For large-scale audits, consider using a more efficient sentiment analysis library or pre-trained model.

def _calculate_response_time(probe_time: str, response_time: str) -> float:
    """
    Calculate the time between probe submission and response.
    
    Args:
        probe_time: ISO format timestamp of probe submission
        response_time: ISO format timestamp of response
        
    Returns:
        Response time in hours
    """
    try:
        probe_dt = datetime.fromisoformat(probe_time)
        response_dt = datetime.fromisoformat(response_time)
        delta = response_dt - probe_dt
        return delta.total_seconds() / 3600  # Convert to hours
    except (ValueError, TypeError) as e:
        logging.error(f"Error calculating response time: {e}")
def _calculate_response_time(probe_time: str, response_time: str) -> Optional[float]:
    """
    Calculate the time between probe submission and response.
    
    Args:
        probe_time: ISO format timestamp of probe submission
        response_time: ISO format timestamp of response
        
    Returns:
        Response time in hours or None if calculation fails
    """
    try:
        probe_dt = datetime.fromisoformat(probe_time)
        response_dt = datetime.fromisoformat(response_time)
        delta = response_dt - probe_dt
        return delta.total_seconds() / 3600  # Convert to hours
    except (ValueError, TypeError) as e:
        logging.error(f"Error calculating response time: {e}")
        return None
        
def _analyze_sentiment(text: str) -> float:
    """
    Analyze the sentiment of response text using NLTK VADER.
    
    Args:
        text: Response text to analyze
        
    Returns:
        Compound sentiment score between -1.0 (negative) and 1.0 (positive).
    """
    if not text:
        return 0.0 # Neutral sentiment for empty text
        
    # Use NLTK VADER to get sentiment scores
    scores = sid.polarity_scores(text)
    
    # Return the compound score, which is a normalized composite score
    return scores['compound']

def analyze_response(response: Dict, probe: Dict) -> Dict:
    """
    Analyze a response to extract metrics.
    
    This function processes the response to extract metrics like response time
    and sentiment score. It immediately discards the actual response content
    after analysis to avoid storing any PII.
    
    Args:
        response: Response dictionary
        probe: Original probe dictionary
        
    Returns:
        Dictionary with analysis results
    """
    # Extract response time
    if 'timestamp' in response and 'timestamp' in probe:
        response_time = _calculate_response_time(
            probe['timestamp'], 
            response['timestamp']
        )
    else:
        response_time = None
        
    # Perform sentiment analysis on the response text
    sentiment_score = _analyze_sentiment(response.get('text', ''))
    
    # Immediately discard the response text to avoid storing PII
    analysis_result = {
        'probe_id': probe.get('id'),
        'variation': probe.get('variation'),
        'response_received': True,
        'response_time_hours': response_time,
        'sentiment_score': sentiment_score
    }
    
    # Important: We do NOT include the actual response text in the result
    return analysis_result
