"""
Response Analysis Module for British Airways Customer Service Responsiveness Bias Audit

This module handles the analysis of customer service responses to detect potential
bias in responsiveness based on perceived identity.
"""

import re
import math
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass

from .constants import (
    RESPONSE_RATE_THRESHOLD,
    RESPONSE_TIME_THRESHOLD,
    SENTIMENT_SCORE_THRESHOLD,
    CONFIDENCE_LEVEL
)


@dataclass
class ResponseMetrics:
    """Container for response metrics."""
    response_rate: float
    avg_response_time: float
    sentiment_score: float
    sample_size: int
    confidence_interval: Tuple[float, float]


@dataclass
class BiasResult:
    """Container for bias detection results."""
    metric_name: str
    group_a_value: float
    group_b_value: float
    difference: float
    threshold: float
    is_biased: bool
    p_value: float
    confidence_interval: Tuple[float, float]


@dataclass
class AuditResult:
    """Container for overall audit results."""
    group_a_metrics: ResponseMetrics
    group_b_metrics: ResponseMetrics
    bias_results: List[BiasResult]
    overall_biased: bool
    timestamp: str
    metadata: Dict


class ResponseAnalyzer:
    """
    Analyzes customer service responses to detect potential bias.
    """
    
    def __init__(self):
        """Initialize the response analyzer."""
        pass
    
    def calculate_response_rate(self, responses: List[Dict]) -> float:
        """
        Calculate the response rate from a list of responses.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Response rate as a float between 0 and 1
        """
        if not responses:
            return 0.0
        
        responded = sum(1 for r in responses if r.get("received_response", False))
        return responded / len(responses)
    
    def calculate_average_response_time(self, responses: List[Dict]) -> float:
        """
        Calculate the average response time in seconds.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Average response time in seconds, or -1 if no responses
        """
        response_times = []
        
        for response in responses:
            if not response.get("received_response", False):
                continue
                
            sent_time = datetime.fromisoformat(response["timestamp"])
            response_time = datetime.fromisoformat(response["response_timestamp"])
            
            # Calculate time difference in seconds
            time_diff = (response_time - sent_time).total_seconds()
            response_times.append(time_diff)
        
        if not response_times:
            return -1.0
            
        return statistics.mean(response_times)
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze the sentiment of a response text.
        
        Args:
            text: Response text to analyze
            
        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        # Simple rule-based sentiment analysis
        # In a real implementation, this would use a proper NLP library
        
        positive_words = [
            "happy", "pleased", "delighted", "glad", "thank", "appreciate",
            "help", "resolve", "solution", "assist", "support", "welcome",
            "pleasure", "apologize", "sorry", "regret"
        ]
        
        negative_words = [
            "unfortunately", "cannot", "unable", "not possible", "difficult",
            "problem", "issue", "complaint", "delay", "inconvenience", 
            "disappointed", "frustration", "failure", "denied", "reject"
        ]
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Count occurrences of positive and negative words
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        # Calculate sentiment score
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
            
        return (positive_count - negative_count) / total_count
    
    def calculate_average_sentiment(self, responses: List[Dict]) -> float:
        """
        Calculate the average sentiment score across responses.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Average sentiment score, or 0 if no responses
        """
        sentiment_scores = []
        
        for response in responses:
            if not response.get("received_response", False) or not response.get("response_text"):
                continue
                
            sentiment = self.analyze_sentiment(response["response_text"])
            sentiment_scores.append(sentiment)
        
        if not sentiment_scores:
            return 0.0
            
        return statistics.mean(sentiment_scores)
    
    def calculate_confidence_interval(self, value: float, sample_size: int, confidence: float = CONFIDENCE_LEVEL) -> Tuple[float, float]:
        """
        Calculate confidence interval for a proportion.
        
        Args:
            value: Proportion value (between 0 and 1)
            sample_size: Sample size
            confidence: Confidence level (default: 0.95)
            
        Returns:
            Tuple containing lower and upper bounds of confidence interval
        """
        if sample_size == 0:
            return (0.0, 0.0)
            
        # For proportions, we use the normal approximation to the binomial
        # z-score for the given confidence level
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        
        z = z_scores.get(confidence, 1.96)
        
        # Standard error of the proportion
        std_error = math.sqrt((value * (1 - value)) / sample_size)
        
        # Calculate confidence interval
        margin = z * std_error
        lower_bound = max(0.0, value - margin)
        upper_bound = min(1.0, value + margin)
        
        return (lower_bound, upper_bound)
    
    def calculate_p_value(self, group_a_value: float, group_b_value: float, 
                         group_a_size: int, group_b_size: int) -> float:
        """
        Calculate p-value for difference between two proportions.
        
        Args:
            group_a_value: Proportion for group A
            group_b_value: Proportion for group B
            group_a_size: Sample size for group A
            group_b_size: Sample size for group B
            
        Returns:
            p-value for the difference
        """
        # Simple approximation using normal distribution
        # In a real implementation, we would use a proper statistical library
        
        if group_a_size == 0 or group_b_size == 0:
            return 1.0
            
        # Pooled proportion
        pooled = ((group_a_value * group_a_size) + (group_b_value * group_b_size)) / (group_a_size + group_b_size)
        
        # Standard error of the difference
        std_error = math.sqrt(pooled * (1 - pooled) * ((1 / group_a_size) + (1 / group_b_size)))
        
        if std_error == 0:
            return 1.0 if group_a_value == group_b_value else 0.0
            
        # Z-score
        z = abs(group_a_value - group_b_value) / std_error
        
        # Approximate p-value using complementary error function
        p_value = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        
        return p_value
    
    def compute_metrics(self, responses: List[Dict], group: str) -> ResponseMetrics:
        """
        Compute all metrics for a group of responses.
        
        Args:
            responses: List of response dictionaries
            group: Group identifier
            
        Returns:
            ResponseMetrics object containing all metrics
        """
        # Filter responses by group
        group_responses = [r for r in responses if r.get("group") == group]
        sample_size = len(group_responses)
        
        if sample_size == 0:
            return ResponseMetrics(
                response_rate=0.0,
                avg_response_time=-1.0,
                sentiment_score=0.0,
                sample_size=0,
                confidence_interval=(0.0, 0.0)
            )
        
        # Calculate metrics
        response_rate = self.calculate_response_rate(group_responses)
        avg_response_time = self.calculate_average_response_time(group_responses)
        sentiment_score = self.calculate_average_sentiment(group_responses)
        
        # Calculate confidence interval for response rate
        confidence_interval = self.calculate_confidence_interval(response_rate, sample_size)
        
        return ResponseMetrics(
            response_rate=response_rate,
            avg_response_time=avg_response_time,
            sentiment_score=sentiment_score,
            sample_size=sample_size,
            confidence_interval=confidence_interval
        )
    
    def detect_bias(self, group_a_metrics: ResponseMetrics, group_b_metrics: ResponseMetrics) -> List[BiasResult]:
        """
        Detect bias between two groups based on their metrics.
        
        Args:
            group_a_metrics: Metrics for group A
            group_b_metrics: Metrics for group B
            
        Returns:
            List of BiasResult objects for each metric
        """
        bias_results = []
        
        # Response rate bias
        response_rate_diff = abs(group_a_metrics.response_rate - group_b_metrics.response_rate)
        response_rate_p_value = self.calculate_p_value(
            group_a_metrics.response_rate, 
            group_b_metrics.response_rate,
            group_a_metrics.sample_size,
            group_b_metrics.sample_size
        )
        
        response_rate_bias = BiasResult(
            metric_name="response_rate",
            group_a_value=group_a_metrics.response_rate,
            group_b_value=group_b_metrics.response_rate,
            difference=response_rate_diff,
            threshold=RESPONSE_RATE_THRESHOLD,
            is_biased=response_rate_diff > RESPONSE_RATE_THRESHOLD and response_rate_p_value < (1 - CONFIDENCE_LEVEL),
            p_value=response_rate_p_value,
            confidence_interval=(
                abs(group_a_metrics.confidence_interval[0] - group_b_metrics.confidence_interval[0]),
                abs(group_a_metrics.confidence_interval[1] - group_b_metrics.confidence_interval[1])
            )
        )
        bias_results.append(response_rate_bias)
        
        # Response time bias (only if both groups have responses)
        if group_a_metrics.avg_response_time > 0 and group_b_metrics.avg_response_time > 0:
            response_time_diff = abs(group_a_metrics.avg_response_time - group_b_metrics.avg_response_time)
            
            # Simplified p-value calculation for response time
            # In a real implementation, we would use a proper t-test
            response_time_p_value = 0.05 if response_time_diff > RESPONSE_TIME_THRESHOLD else 0.5
            
            response_time_bias = BiasResult(
                metric_name="response_time",
                group_a_value=group_a_metrics.avg_response_time,
                group_b_value=group_b_metrics.avg_response_time,
                difference=response_time_diff,
                threshold=RESPONSE_TIME_THRESHOLD,
                is_biased=response_time_diff > RESPONSE_TIME_THRESHOLD,
                p_value=response_time_p_value,
                confidence_interval=(0.0, 0.0)  # Simplified
            )
            bias_results.append(response_time_bias)
        
        # Sentiment score bias (only if both groups have responses)
        if group_a_metrics.sentiment_score != 0 or group_b_metrics.sentiment_score != 0:
            sentiment_diff = abs(group_a_metrics.sentiment_score - group_b_metrics.sentiment_score)
            
            # Simplified p-value calculation for sentiment
            sentiment_p_value = 0.05 if sentiment_diff > SENTIMENT_SCORE_THRESHOLD else 0.5
            
            sentiment_bias = BiasResult(
                metric_name="sentiment",
                group_a_value=group_a_metrics.sentiment_score,
                group_b_value=group_b_metrics.sentiment_score,
                difference=sentiment_diff,
                threshold=SENTIMENT_SCORE_THRESHOLD,
                is_biased=sentiment_diff > SENTIMENT_SCORE_THRESHOLD,
                p_value=sentiment_p_value,
                confidence_interval=(0.0, 0.0)  # Simplified
            )
            bias_results.append(sentiment_bias)
        
        return bias_results
    
    def analyze_responses(self, responses: List[Dict]) -> AuditResult:
        """
        Analyze responses and detect bias.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            AuditResult object containing analysis results
        """
        # Compute metrics for each group
        group_a_metrics = self.compute_metrics(responses, "group_a")
        group_b_metrics = self.compute_metrics(responses, "group_b")
        
        # Detect bias
        bias_results = self.detect_bias(group_a_metrics, group_b_metrics)
        
        # Determine overall bias
        overall_biased = any(result.is_biased for result in bias_results)
        
        # Create audit result
        audit_result = AuditResult(
            group_a_metrics=group_a_metrics,
            group_b_metrics=group_b_metrics,
            bias_results=bias_results,
            overall_biased=overall_biased,
            timestamp=datetime.now().isoformat(),
            metadata={
                "total_responses": len(responses),
                "group_a_count": group_a_metrics.sample_size,
                "group_b_count": group_b_metrics.sample_size
            }
        )
        
        return audit_result


def analyze_responses(responses: List[Dict]) -> AuditResult:
    """
    Convenience function to analyze responses.
    
    Args:
        responses: List of response dictionaries
        
    Returns:
        AuditResult object containing analysis results
    """
    analyzer = ResponseAnalyzer()
    return analyzer.analyze_responses(responses)