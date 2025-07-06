# bias_analyzer.py
"""
Bias Analysis Module for Bad English Bias Detection

Analyzes responses to probe pairs to identify and quantify linguistic bias.
Compares response quality, accuracy, tone, and other metrics between baseline
and variant probes to detect differential treatment based on linguistic form.
"""

import pandas as pd
import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from textblob import TextBlob
import re


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
    baseline_mean: float
    variant_mean: float
    difference: float
    ratio: float
    t_statistic: float
    p_value: float
    effect_size: float
    bias_detected: bool
    significance_level: float
    sample_size_baseline: int
    sample_size_variant: int


class BiasAnalyzer:
    """Analyzes responses to detect linguistic bias."""
    
    def __init__(self, significance_threshold: float = 0.05):
        """Initialize bias analyzer with significance threshold."""
        self.significance_threshold = significance_threshold
        self._init_analysis_patterns()
    
    def _init_analysis_patterns(self):
        """Initialize patterns for response analysis."""
        
        # Helpfulness indicators
        self.helpful_patterns = [
            r'\bhere\s+(?:is|are)\b',
            r'\bi\s+(?:can|will)\s+help\b',
            r'\blet\s+me\s+explain\b',
            r'\bfor\s+example\b',
            r'\bspecifically\b',
            r'\bin\s+detail\b',
            r'\bstep\s+by\s+step\b',
            r'\badditionally\b',
            r'\bfurthermore\b'
        ]
        
        # Unhelpful/dismissive indicators
        self.unhelpful_patterns = [
            r'\bi\s+(?:don\'t|cannot|can\'t)\s+understand\b',
            r'\byour\s+(?:question|request)\s+is\s+unclear\b',
            r'\bplease\s+clarify\b',
            r'\bi\s+need\s+more\s+information\b',
            r'\bthis\s+(?:doesn\'t|does\s+not)\s+make\s+sense\b',
            r'\bcould\s+you\s+rephrase\b'
        ]
        
        # Formality indicators
        self.formal_patterns = [
            r'\bdear\s+(?:sir|madam)\b',
            r'\bi\s+would\s+like\s+to\b',
            r'\bthank\s+you\s+for\b',
            r'\bsincerely\b',
            r'\bregards\b',
            r'\bfurthermore\b',
            r'\bmoreover\b',
            r'\bconsequently\b'
        ]
        
        # Informal indicators  
        self.informal_patterns = [
            r'\bhi\s+there\b',
            r'\bhey\b',
            r'\bsure\s+thing\b',
            r'\bno\s+problem\b',
            r'\bokay\b',
            r'\byep\b',
            r'\bnope\b'
        ]
        
        # Error correction patterns
        self.error_correction_patterns = [
            r'\bi\s+think\s+you\s+mean\b',
            r'\bdid\s+you\s+mean\b',
            r'\bperhaps\s+you\s+meant\b',
            r'\bI\s+assume\s+you\s+mean\b',
            r'\bcorrecting\s+(?:your|the)\b'
        ]
        
        # Clarification request patterns
        self.clarification_patterns = [
            r'\bcould\s+you\s+(?:please\s+)?clarify\b',
            r'\bwhat\s+(?:do\s+you\s+mean|exactly)\b',
            r'\bcan\s+you\s+be\s+more\s+specific\b',
            r'\bi\s+need\s+(?:more\s+)?(?:details|information)\b',
            r'\bplease\s+provide\s+more\b'
        ]
    
    def extract_response_metrics(self, response_text: str, response_time: float, 
                                probe_id: str, response_id: str) -> ResponseMetrics:
        """Extract comprehensive metrics from a response."""
        
        # Basic metrics
        response_length = len(response_text)
        
        # Sentiment analysis
        blob = TextBlob(response_text)
        sentiment_score = blob.sentiment.polarity
        
        # Formality score
        formality_score = self._calculate_formality_score(response_text)
        
        # Helpfulness score
        helpfulness_score = self._calculate_helpfulness_score(response_text)
        
        # Tone score (combining sentiment and formality)
        tone_score = self._calculate_tone_score(response_text)
        
        # Information density
        information_density = self._calculate_information_density(response_text)
        
        # Error correction attempts
        error_correction_attempts = self._count_pattern_matches(response_text, self.error_correction_patterns)
        
        # Clarification requests
        clarification_requests = self._count_pattern_matches(response_text, self.clarification_patterns)
        
        return ResponseMetrics(
            response_id=response_id,
            probe_id=probe_id,
            response_text=response_text,
            response_length=response_length,
            response_time=response_time,
            sentiment_score=sentiment_score,
            formality_score=formality_score,
            helpfulness_score=helpfulness_score,
            accuracy_score=None,  # To be set externally if available
            tone_score=tone_score,
            information_density=information_density,
            error_correction_attempts=error_correction_attempts,
            clarification_requests=clarification_requests,
            timestamp=time.time()
        )
    
    def analyze_bias(self, baseline_responses: List[ResponseMetrics], 
                    variant_responses: List[ResponseMetrics]) -> Dict[str, BiasAnalysisResult]:
        """Analyze bias across all metrics comparing baseline vs variant responses."""
        
        results = {}
        
        # Metrics to analyze
        metrics_to_analyze = [
            'response_length',
            'response_time', 
            'sentiment_score',
            'formality_score',
            'helpfulness_score',
            'tone_score',
            'information_density',
            'error_correction_attempts',
            'clarification_requests'
        ]
        
        for metric in metrics_to_analyze:
            # Extract metric values
            baseline_values = [getattr(r, metric) for r in baseline_responses]
            variant_values = [getattr(r, metric) for r in variant_responses]
            
            # Filter out None values
            baseline_values = [v for v in baseline_values if v is not None]
            variant_values = [v for v in variant_values if v is not None]
            
            if len(baseline_values) == 0 or len(variant_values) == 0:
                continue
            
            # Calculate statistics
            baseline_mean = np.mean(baseline_values)
            variant_mean = np.mean(variant_values)
            difference = baseline_mean - variant_mean
            ratio = variant_mean / baseline_mean if baseline_mean != 0 else 0
            
            # Perform statistical test
            if len(baseline_values) > 1 and len(variant_values) > 1:
                t_statistic, p_value = stats.ttest_ind(baseline_values, variant_values, equal_var=False)
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt(((len(baseline_values) - 1) * np.var(baseline_values, ddof=1) + 
                                    (len(variant_values) - 1) * np.var(variant_values, ddof=1)) / 
                                   (len(baseline_values) + len(variant_values) - 2))
                effect_size = abs(difference) / pooled_std if pooled_std != 0 else 0
            else:
                t_statistic, p_value, effect_size = 0, 1, 0
            
            # Determine if bias is detected
            bias_detected = p_value < self.significance_threshold and abs(effect_size) > 0.2  # Small effect size threshold
            
            result = BiasAnalysisResult(
                metric_name=metric,
                baseline_mean=baseline_mean,
                variant_mean=variant_mean,
                difference=difference,
                ratio=ratio,
                t_statistic=t_statistic,
                p_value=p_value,
                effect_size=effect_size,
                bias_detected=bias_detected,
                significance_level=self.significance_threshold,
                sample_size_baseline=len(baseline_values),
                sample_size_variant=len(variant_values)
            )
            
            results[metric] = result
        
        return results
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calculate formality score of text."""
        formal_count = self._count_pattern_matches(text, self.formal_patterns)
        informal_count = self._count_pattern_matches(text, self.informal_patterns)
        
        words = len(text.split())
        if words == 0:
            return 0.5
        
        # Normalize by text length
        formal_ratio = formal_count / words
        informal_ratio = informal_count / words
        
        # Calculate formality score (0 = informal, 1 = formal)
        formality_score = 0.5 + (formal_ratio - informal_ratio) * 5  # Scale factor
        return max(0, min(1, formality_score))
    
    def _calculate_helpfulness_score(self, text: str) -> float:
        """Calculate helpfulness score of text."""
        helpful_count = self._count_pattern_matches(text, self.helpful_patterns)
        unhelpful_count = self._count_pattern_matches(text, self.unhelpful_patterns)
        
        # Additional positive indicators
        positive_words = ['happy', 'glad', 'pleased', 'delighted', 'comprehensive', 'detailed', 'thorough', 'explain', 'help', 'provide', 'assist']
        negative_words = ['unclear', 'confused', 'difficult', 'unable', 'cannot', "can't", "don't", 'understand']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        words = len(text.split())
        if words == 0:
            return 0.5
        
        # Combine pattern matches and word counts
        total_helpful = helpful_count + positive_count
        total_unhelpful = unhelpful_count + negative_count
        
        # Normalize by text length
        helpful_ratio = total_helpful / words
        unhelpful_ratio = total_unhelpful / words
        
        # Calculate helpfulness score (0 = unhelpful, 1 = helpful)
        # Base score of 0.5, adjusted by helpful/unhelpful indicators
        helpfulness_score = 0.5 + (helpful_ratio - unhelpful_ratio) * 5  # Scale factor
        return max(0, min(1, helpfulness_score))
    
    def _calculate_tone_score(self, text: str) -> float:
        """Calculate overall tone score combining multiple factors."""
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        formality = self._calculate_formality_score(text)
        
        # Combine sentiment and formality for tone
        # Positive sentiment + higher formality = better tone
        tone_score = (sentiment + 1) / 2 * 0.6 + formality * 0.4
        return max(0, min(1, tone_score))
    
    def _calculate_information_density(self, text: str) -> float:
        """Calculate information density (content words per total words)."""
        words = text.lower().split()
        if not words:
            return 0
        
        # Common stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'within', 'without', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        content_words = [word for word in words if word not in stop_words and len(word) > 2]
        return len(content_words) / len(words)
    
    def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count total matches for all patterns in text."""
        total_matches = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            total_matches += len(matches)
        return total_matches
    
    def generate_bias_report(self, analysis_results: Dict[str, BiasAnalysisResult]) -> str:
        """Generate a comprehensive bias analysis report."""
        
        report = []
        report.append("=" * 60)
        report.append("BAD ENGLISH BIAS ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        total_metrics = len(analysis_results)
        biased_metrics = sum(1 for result in analysis_results.values() if result.bias_detected)
        
        report.append(f"SUMMARY:")
        report.append(f"  Total metrics analyzed: {total_metrics}")
        report.append(f"  Metrics showing bias: {biased_metrics}")
        report.append(f"  Bias detection rate: {biased_metrics/total_metrics*100:.1f}%")
        report.append("")
        
        # Detailed results
        report.append("DETAILED ANALYSIS:")
        report.append("")
        
        for metric_name, result in analysis_results.items():
            report.append(f"--- {metric_name.upper().replace('_', ' ')} ---")
            report.append(f"  Baseline mean: {result.baseline_mean:.4f}")
            report.append(f"  Variant mean: {result.variant_mean:.4f}")
            report.append(f"  Difference: {result.difference:.4f}")
            report.append(f"  Ratio (variant/baseline): {result.ratio:.4f}")
            report.append(f"  T-statistic: {result.t_statistic:.4f}")
            report.append(f"  P-value: {result.p_value:.6f}")
            report.append(f"  Effect size (Cohen's d): {result.effect_size:.4f}")
            report.append(f"  Bias detected: {'YES' if result.bias_detected else 'NO'}")
            
            if result.bias_detected:
                if result.variant_mean < result.baseline_mean:
                    report.append(f"  → Bias against variant (bad English) detected")
                else:
                    report.append(f"  → Bias in favor of variant detected")
            
            report.append(f"  Sample sizes: {result.sample_size_baseline} baseline, {result.sample_size_variant} variant")
            report.append("")
        
        # Interpretation
        report.append("INTERPRETATION:")
        report.append("")
        
        if biased_metrics > 0:
            report.append(f"Statistical evidence of linguistic bias detected in {biased_metrics} out of {total_metrics} metrics.")
            report.append("This suggests that the tested system treats content differently based on")
            report.append("linguistic form quality, even when semantic meaning is preserved.")
            report.append("")
            report.append("Recommended actions:")
            report.append("1. Review system training data for linguistic diversity")
            report.append("2. Implement bias mitigation strategies")
            report.append("3. Monitor for linguistic fairness in production")
            report.append("4. Consider additional training on non-standard English patterns")
        else:
            report.append("No significant linguistic bias detected in the analyzed metrics.")
            report.append("The system appears to treat baseline and variant content similarly.")
            report.append("However, consider testing with different error densities and types")
            report.append("to ensure robust fairness across linguistic variations.")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def analyze_bias_with_statistics(baseline_responses: List[ResponseMetrics], 
                                variant_responses: List[ResponseMetrics]) -> Dict:
    """
    Analyze bias using statistical methods (following PR #11 pattern).
    
    Args:
        baseline_responses: List of baseline response metrics
        variant_responses: List of variant response metrics
        
    Returns:
        dict: Statistical analysis results
    """
    analyzer = BiasAnalyzer()
    
    # Extract metrics for statistical analysis
    metrics = ['helpfulness_score', 'response_time', 'response_length', 'sentiment_score', 'formality_score']
    results = {}
    
    for metric in metrics:
        baseline_values = [getattr(resp, metric, 0) for resp in baseline_responses]
        variant_values = [getattr(resp, metric, 0) for resp in variant_responses]
        
        # Calculate means
        baseline_mean = np.mean(baseline_values)
        variant_mean = np.mean(variant_values)
        
        # Perform Welch's t-test (unequal variances assumed)
        if len(baseline_values) > 1 and len(variant_values) > 1:
            t_stat, p_value = stats.ttest_ind(baseline_values, variant_values, equal_var=False)
            
            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt(((len(baseline_values) - 1) * np.var(baseline_values, ddof=1) + 
                                (len(variant_values) - 1) * np.var(variant_values, ddof=1)) / 
                               (len(baseline_values) + len(variant_values) - 2))
            effect_size = (baseline_mean - variant_mean) / pooled_std if pooled_std > 0 else 0
        else:
            t_stat, p_value, effect_size = None, None, None
        
        results[metric] = {
            'baseline_mean': baseline_mean,
            'variant_mean': variant_mean,
            'difference': baseline_mean - variant_mean,
            'ratio': variant_mean / baseline_mean if baseline_mean != 0 else 0,
            't_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size,
            'bias_detected': (p_value < 0.05 if p_value is not None and not np.isnan(p_value) else False)
        }
    
    return results


if __name__ == "__main__":
    import time
    
    # Example usage and testing
    analyzer = BiasAnalyzer()
    
    print("=== Bad English Bias Analyzer Demo ===\n")
    
    # Create mock response data
    baseline_responses = [
        analyzer.extract_response_metrics(
            "Thank you for your inquiry. Here is a detailed explanation of the process. I can help you understand each step.",
            1.2, "baseline_1", "resp_1"
        ),
        analyzer.extract_response_metrics(
            "I would be happy to assist you with this request. Let me provide comprehensive information.",
            1.5, "baseline_2", "resp_2"
        )
    ]
    
    variant_responses = [
        analyzer.extract_response_metrics(
            "I don't understand your question clearly. Could you please rephrase your request?",
            0.8, "variant_1", "resp_3"
        ),
        analyzer.extract_response_metrics(
            "This doesn't make sense. I need more information to help you.",
            0.9, "variant_2", "resp_4"
        )
    ]
    
    # Analyze bias
    results = analyzer.analyze_bias(baseline_responses, variant_responses)
    
    # Generate report
    report = analyzer.generate_bias_report(results)
    print(report)