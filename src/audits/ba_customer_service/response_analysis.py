"""
Response Analysis Module for British Airways Customer Service Responsiveness Bias Audit

This module implements functions for analyzing customer service responses,
including response rate, timing, and sentiment analysis.
"""

import time
import statistics
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math
from datetime import datetime

# Assuming these are provided by the framework
from core.utils import sentiment_analyzer
from core.stats import calculate_statistical_significance

from .constants import (
    BIAS_THRESHOLD,
    CONFIDENCE_LEVEL,
    SentimentCategory,
    SENTIMENT_THRESHOLDS
)


@dataclass
class Response:
    """
    Represents a customer service response.
    """
    probe_id: str
    received: bool
    timestamp: Optional[float] = None
    response_time_hours: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_category: Optional[SentimentCategory] = None
    metadata: Dict = None


def calculate_response_rate(responses: List[Response], variation: str) -> float:
    """
    Calculate the response rate for a specific variation.
    
    Args:
        responses: List of Response objects
        variation: Variation to calculate response rate for
        
    Returns:
        Response rate as a float between 0 and 1
    """
    variation_responses = [r for r in responses if r.metadata.get("variation") == variation]
    
    if not variation_responses:
        return 0.0
    
    received_count = sum(1 for r in variation_responses if r.received)
    return received_count / len(variation_responses)


def calculate_response_time_stats(responses: List[Response], variation: str) -> Dict[str, float]:
    """
    Calculate response time statistics for a specific variation.
    
    Args:
        responses: List of Response objects
        variation: Variation to calculate statistics for
        
    Returns:
        Dictionary with response time statistics
    """
    # Filter responses by variation and only include those that were received
    variation_responses = [
        r for r in responses 
        if r.metadata.get("variation") == variation and r.received and r.response_time_hours is not None
    ]
    
    if not variation_responses:
        return {
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "std_dev": None
        }
    
    response_times = [r.response_time_hours for r in variation_responses]
    
    return {
        "mean": statistics.mean(response_times),
        "median": statistics.median(response_times),
        "min": min(response_times),
        "max": max(response_times),
        "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
    }


def calculate_sentiment_stats(responses: List[Response], variation: str) -> Dict[str, Any]:
    """
    Calculate sentiment statistics for a specific variation.
    
    Args:
        responses: List of Response objects
        variation: Variation to calculate statistics for
        
    Returns:
        Dictionary with sentiment statistics
    """
    # Filter responses by variation and only include those that were received
    variation_responses = [
        r for r in responses 
        if r.metadata.get("variation") == variation and r.received and r.sentiment_score is not None
    ]
    
    if not variation_responses:
        return {
            "mean": None,
            "median": None,
            "category_counts": {
                SentimentCategory.NEGATIVE.value: 0,
                SentimentCategory.NEUTRAL.value: 0,
                SentimentCategory.POSITIVE.value: 0
            }
        }
    
    sentiment_scores = [r.sentiment_score for r in variation_responses]
    
    # Count responses by sentiment category
    category_counts = {
        SentimentCategory.NEGATIVE.value: 0,
        SentimentCategory.NEUTRAL.value: 0,
        SentimentCategory.POSITIVE.value: 0
    }
    
    for r in variation_responses:
        if r.sentiment_category:
            category_counts[r.sentiment_category.value] += 1
    
    return {
        "mean": statistics.mean(sentiment_scores),
        "median": statistics.median(sentiment_scores),
        "category_counts": category_counts
    }


def analyze_response_text(text: str) -> Tuple[float, SentimentCategory]:
    """
    Analyze the sentiment of a response text.
    
    Args:
        text: Response text to analyze
        
    Returns:
        Tuple of (sentiment_score, sentiment_category)
    """
    # Use the framework's sentiment analyzer to get a score
    sentiment_score = sentiment_analyzer.analyze(text)
    
    # Determine sentiment category based on thresholds
    sentiment_category = None
    for category, threshold in SENTIMENT_THRESHOLDS.items():
        if sentiment_score <= threshold:
            sentiment_category = category
            break
    
    return sentiment_score, sentiment_category


def process_response(
    probe_id: str, 
    response_text: str, 
    received_timestamp: float,
    probe_metadata: Dict
) -> Response:
    """
    Process a customer service response.
    
    Args:
        probe_id: ID of the probe that received this response
        response_text: Text content of the response
        received_timestamp: Timestamp when the response was received
        probe_metadata: Metadata from the original probe
        
    Returns:
        Response object with analysis results
    """
    # Calculate response time in hours
    probe_timestamp = probe_metadata.get("timestamp", 0)
    response_time_hours = (received_timestamp - probe_timestamp) / 3600
    
    # Analyze sentiment
    sentiment_score, sentiment_category = analyze_response_text(response_text)
    
    # Create response object
    response = Response(
        probe_id=probe_id,
        received=True,
        timestamp=received_timestamp,
        response_time_hours=response_time_hours,
        sentiment_score=sentiment_score,
        sentiment_category=sentiment_category,
        metadata={
            "variation": probe_metadata.get("variation"),
            "name": probe_metadata.get("name"),
            "processed_at": datetime.now().isoformat()
        }
    )
    
    # Important: Immediately discard the raw response text after analysis
    # to avoid storing any PII that might be in the response
    del response_text
    
    return response


def detect_bias(responses: List[Response]) -> Dict[str, Any]:
    """
    Detect bias in customer service responses.
    
    Args:
        responses: List of Response objects
        
    Returns:
        Dictionary with bias detection results
    """
    results = {
        "bias_detected": False,
        "metrics": {},
        "statistical_significance": {}
    }
    
    # Calculate response rates
    western_rate = calculate_response_rate(responses, "western")
    non_western_rate = calculate_response_rate(responses, "non_western")
    rate_difference = abs(western_rate - non_western_rate)
    
    results["metrics"]["response_rate"] = {
        "western": western_rate,
        "non_western": non_western_rate,
        "difference": rate_difference,
        "bias_detected": rate_difference > BIAS_THRESHOLD["response_rate"]
    }
    
    # Calculate response time statistics
    western_time_stats = calculate_response_time_stats(responses, "western")
    non_western_time_stats = calculate_response_time_stats(responses, "non_western")
    
    if western_time_stats["mean"] is not None and non_western_time_stats["mean"] is not None:
        time_difference = abs(western_time_stats["mean"] - non_western_time_stats["mean"])
        
        results["metrics"]["response_time"] = {
            "western": western_time_stats,
            "non_western": non_western_time_stats,
            "difference": time_difference,
            "bias_detected": time_difference > BIAS_THRESHOLD["response_time"]
        }
    
    # Calculate sentiment statistics
    western_sentiment_stats = calculate_sentiment_stats(responses, "western")
    non_western_sentiment_stats = calculate_sentiment_stats(responses, "non_western")
    
    if western_sentiment_stats["mean"] is not None and non_western_sentiment_stats["mean"] is not None:
        sentiment_difference = abs(western_sentiment_stats["mean"] - non_western_sentiment_stats["mean"])
        
        results["metrics"]["sentiment"] = {
            "western": western_sentiment_stats,
            "non_western": non_western_sentiment_stats,
            "difference": sentiment_difference,
            "bias_detected": sentiment_difference > BIAS_THRESHOLD["sentiment"]
        }
    
    # Calculate statistical significance
    for metric, data in results["metrics"].items():
        if "bias_detected" in data and data["bias_detected"]:
            # Only calculate significance if bias is detected
            significance = calculate_statistical_significance(
                group_a_data=[1 if r.received else 0 for r in responses if r.metadata.get("variation") == "western"],
                group_b_data=[1 if r.received else 0 for r in responses if r.metadata.get("variation") == "non_western"],
                confidence_level=CONFIDENCE_LEVEL
            )
            
            results["statistical_significance"][metric] = significance
            
            # Update overall bias detection result
            if significance["significant"]:
                results["bias_detected"] = True
    
    return results


def calculate_minimum_sample_size(
    effect_size: float = 0.15,
    power: float = 0.8,
    alpha: float = 0.05
) -> int:
    """
    Calculate the minimum sample size needed to detect the specified effect size.
    
    Args:
        effect_size: Minimum effect size to detect
        power: Statistical power (1 - β)
        alpha: Significance level (Type I error rate)
        
    Returns:
        Minimum sample size per group
    """
    # This is a simplified calculation for a two-sample proportion test
    z_alpha = 1.96  # z-score for alpha=0.05
    z_beta = 0.84   # z-score for power=0.8
    
    # Calculate sample size per group
    n = ((z_alpha + z_beta)**2 * 2 * 0.5 * (1 - 0.5)) / (effect_size**2)
    
    # Round up to the nearest integer
    return math.ceil(n)