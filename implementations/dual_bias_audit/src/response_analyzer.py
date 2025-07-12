"""
Response Analyzer Module for Dual Bias Audit

Analyzes responses to probe pairs to identify and quantify bias.
Extracts metrics and performs statistical analysis to detect differential treatment.
"""

import time
import logging
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
import html

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available, sentiment analysis will be limited")


@dataclass
class ResponseMetrics:
    """Metrics extracted from a system response."""
    response_id: str
    probe_id: str
    response_text: str
    response_length: int
    response_time: float
    sentiment_score: float
    formality_score: float
    helpfulness_score: float
    accuracy_score: Optional[float]
    tone_score: float
    information_density: float
    error_correction_attempts: int
    clarification_requests: int
    timestamp: float
    
    @property
    def is_helpful(self) -> bool:
        """Determine if response is helpful based on helpfulness score."""
        return self.helpfulness_score > 0.5


@dataclass
class BiasAnalysisResult:
    """Results of bias analysis for a specific metric."""
    metric_name: str
    group_a_mean: float
    group_b_mean: float
    difference: float
    ratio: float
    t_statistic: float
    p_value: float
    effect_size: float  # Cohen's d
    bias_detected: bool
    significance_level: float
    sample_size_group_a: int
    sample_size_group_b: int