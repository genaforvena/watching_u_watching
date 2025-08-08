"""
Statistical analysis module for alignment probes.

This module provides statistical testing, power analysis, and comprehensive
statistical validation for alignment probe experiments.
"""

import statistics
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class StatisticalTest:
    """
    Result of a statistical test.
    """
    test_name: str
    test_statistic: float
    p_value: float
    is_significant: bool
    confidence_level: float
    interpretation: str
    effect_size: Optional[float] = None
    power: Optional[float] = None


class StatisticalAnalysis:
    """
    Comprehensive statistical analysis for alignment probe results.
    """
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical analysis.
        
        Args:
            alpha: Significance level (default 0.05 for 95% confidence)
        """
        self.alpha = alpha
        self.confidence_level = 1 - alpha
        
    def t_test_one_sample(self, scores: List[float], 
                         expected_mean: float) -> StatisticalTest:
        """
        Perform one-sample t-test to compare scores against expected mean.
        
        Args:
            scores: List of observed scores
            expected_mean: Expected/hypothesized mean value
            
        Returns:
            StatisticalTest result
        """
        if len(scores) < 2:
            return StatisticalTest(
                test_name="one_sample_t_test",
                test_statistic=0,
                p_value=1.0,
                is_significant=False,
                confidence_level=self.confidence_level,
                interpretation="Insufficient data for t-test"
            )
        
        sample_mean = statistics.mean(scores)
        sample_std = statistics.stdev(scores)
        n = len(scores)
        
        # Calculate t-statistic
        t_stat = (sample_mean - expected_mean) / (sample_std / math.sqrt(n))
        
        # Approximate p-value (simplified)
        # In practice, would use scipy.stats or proper t-distribution
        df = n - 1
        p_value = self._approximate_t_test_p_value(abs(t_stat), df)
        
        is_significant = p_value < self.alpha
        
        # Effect size (Cohen's d)
        effect_size = (sample_mean - expected_mean) / sample_std
        
        interpretation = self._interpret_t_test(t_stat, p_value, is_significant, effect_size)
        
        return StatisticalTest(
            test_name="one_sample_t_test",
            test_statistic=t_stat,
            p_value=p_value,
            is_significant=is_significant,
            confidence_level=self.confidence_level,
            interpretation=interpretation,
            effect_size=effect_size
        )
    
    def t_test_two_sample(self, group1: List[float], 
                         group2: List[float],
                         group1_name: str = "Group 1",
                         group2_name: str = "Group 2") -> StatisticalTest:
        """
        Perform two-sample t-test to compare two groups.
        
        Args:
            group1: Scores from first group
            group2: Scores from second group
            group1_name: Name for first group
            group2_name: Name for second group
            
        Returns:
            StatisticalTest result
        """
        if len(group1) < 2 or len(group2) < 2:
            return StatisticalTest(
                test_name="two_sample_t_test",
                test_statistic=0,
                p_value=1.0,
                is_significant=False,
                confidence_level=self.confidence_level,
                interpretation="Insufficient data for two-sample t-test"
            )
        
        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)
        var1 = statistics.variance(group1)
        var2 = statistics.variance(group2)
        n1 = len(group1)
        n2 = len(group2)
        
        # Pooled standard error
        pooled_se = math.sqrt(var1/n1 + var2/n2)
        
        # t-statistic
        t_stat = (mean1 - mean2) / pooled_se if pooled_se > 0 else 0
        
        # Degrees of freedom (Welch's approximation)
        if var1 > 0 and var2 > 0:
            df = ((var1/n1 + var2/n2)**2) / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))
        else:
            df = n1 + n2 - 2
        
        p_value = self._approximate_t_test_p_value(abs(t_stat), df)
        is_significant = p_value < self.alpha
        
        # Effect size (Cohen's d)
        pooled_std = math.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        effect_size = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
        
        interpretation = self._interpret_two_sample_t_test(
            t_stat, p_value, is_significant, effect_size, mean1, mean2, 
            group1_name, group2_name
        )
        
        return StatisticalTest(
            test_name="two_sample_t_test",
            test_statistic=t_stat,
            p_value=p_value,
            is_significant=is_significant,
            confidence_level=self.confidence_level,
            interpretation=interpretation,
            effect_size=effect_size
        )
    
    def _approximate_t_test_p_value(self, t_abs: float, df: float) -> float:
        """
        Approximate p-value for t-test (simplified implementation).
        
        Args:
            t_abs: Absolute value of t-statistic
            df: Degrees of freedom
            
        Returns:
            Approximate two-tailed p-value
        """
        # Very simplified approximation - in practice use scipy.stats
        if df < 1:
            return 1.0
        
        # Rough approximation using normal distribution for large df
        if df >= 30:
            # Use standard normal approximation
            if t_abs < 1.96:
                return 0.05 + (1.96 - t_abs) * 0.4  # Rough scaling
            else:
                return max(0.001, 0.05 - (t_abs - 1.96) * 0.02)
        else:
            # Rough t-distribution approximation
            critical_values = {5: 2.571, 10: 2.228, 20: 2.086, 30: 2.042}
            closest_df = min(critical_values.keys(), key=lambda x: abs(x - df))
            critical_t = critical_values[closest_df]
            
            if t_abs < critical_t:
                return 0.05 + (critical_t - t_abs) * 0.3
            else:
                return max(0.001, 0.05 - (t_abs - critical_t) * 0.02)
    
    def _interpret_t_test(self, t_stat: float, p_value: float, 
                         is_significant: bool, effect_size: float) -> str:
        """
        Generate interpretation for one-sample t-test.
        """
        significance_text = "significant" if is_significant else "not significant"
        direction = "higher" if t_stat > 0 else "lower"
        
        effect_interpretation = self._interpret_effect_size(effect_size)
        
        return (f"The difference is {significance_text} (p={p_value:.4f}). "
                f"Sample mean is {direction} than expected with {effect_interpretation} effect size.")
    
    def _interpret_two_sample_t_test(self, t_stat: float, p_value: float,
                                   is_significant: bool, effect_size: float,
                                   mean1: float, mean2: float,
                                   group1_name: str, group2_name: str) -> str:
        """
        Generate interpretation for two-sample t-test.
        """
        significance_text = "significant" if is_significant else "not significant"
        higher_group = group1_name if mean1 > mean2 else group2_name
        
        effect_interpretation = self._interpret_effect_size(effect_size)
        
        return (f"The difference between groups is {significance_text} (p={p_value:.4f}). "
                f"{higher_group} has higher scores with {effect_interpretation} effect size.")
    
    def _interpret_effect_size(self, effect_size: float) -> str:
        """
        Interpret Cohen's d effect size.
        """
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            return "negligible"
        elif abs_effect < 0.5:
            return "small"
        elif abs_effect < 0.8:
            return "medium"
        else:
            return "large"
    
    def power_analysis(self, effect_size: float, sample_size: int,
                      alpha: Optional[float] = None) -> Dict:
        """
        Perform power analysis for given effect size and sample size.
        
        Args:
            effect_size: Expected Cohen's d effect size
            sample_size: Sample size for each group
            alpha: Significance level (uses instance default if None)
            
        Returns:
            Dict containing power analysis results
        """
        alpha = alpha or self.alpha
        
        # Simplified power calculation for t-test
        # In practice, would use scipy.stats.power
        
        # Critical t-value approximation
        if sample_size >= 30:
            critical_t = 1.96  # Normal approximation
        else:
            # Rough t-distribution critical values
            critical_values = {5: 2.571, 10: 2.228, 20: 2.086, 30: 2.042}
            closest_n = min(critical_values.keys(), key=lambda x: abs(x - sample_size))
            critical_t = critical_values[closest_n]
        
        # Non-centrality parameter
        ncp = effect_size * math.sqrt(sample_size / 2)
        
        # Approximate power calculation
        # This is a very simplified version
        if ncp > critical_t:
            power = 0.8 + min(0.19, (ncp - critical_t) * 0.1)
        else:
            power = max(0.05, 0.8 - (critical_t - ncp) * 0.2)
        
        power = max(0.0, min(1.0, power))
        
        return {
            'power': power,
            'effect_size': effect_size,
            'sample_size': sample_size,
            'alpha': alpha,
            'critical_t': critical_t,
            'interpretation': self._interpret_power(power)
        }
    
    def _interpret_power(self, power: float) -> str:
        """
        Interpret statistical power value.
        """
        if power >= 0.8:
            return "adequate"
        elif power >= 0.6:
            return "marginal"
        else:
            return "inadequate"
    
    def sample_size_calculation(self, effect_size: float, 
                              desired_power: float = 0.8,
                              alpha: Optional[float] = None) -> Dict:
        """
        Calculate required sample size for desired power.
        
        Args:
            effect_size: Expected Cohen's d effect size
            desired_power: Desired statistical power (default 0.8)
            alpha: Significance level (uses instance default if None)
            
        Returns:
            Dict containing sample size recommendation
        """
        alpha = alpha or self.alpha
        
        # Simplified sample size calculation
        # This is a rough approximation - in practice use scipy.stats
        
        if effect_size == 0:
            return {
                'recommended_sample_size': float('inf'),
                'interpretation': "Cannot detect zero effect size"
            }
        
        # Rough formula based on standard tables
        if abs(effect_size) >= 0.8:  # Large effect
            base_n = 15
        elif abs(effect_size) >= 0.5:  # Medium effect  
            base_n = 25
        elif abs(effect_size) >= 0.2:  # Small effect
            base_n = 100
        else:  # Very small effect
            base_n = 400
        
        # Adjust for desired power
        power_multiplier = desired_power / 0.8  # Base calculation assumes 80% power
        adjusted_n = int(base_n * power_multiplier * power_multiplier)
        
        # Adjust for alpha level
        if alpha < 0.05:
            adjusted_n = int(adjusted_n * 1.3)
        elif alpha > 0.05:
            adjusted_n = int(adjusted_n * 0.8)
        
        return {
            'recommended_sample_size': adjusted_n,
            'effect_size': effect_size,
            'desired_power': desired_power,
            'alpha': alpha,
            'interpretation': f"Need ~{adjusted_n} samples per group for {desired_power*100:.0f}% power"
        }
    
    def multiple_comparisons_correction(self, p_values: List[float],
                                      method: str = "bonferroni") -> Dict:
        """
        Apply multiple comparisons correction to p-values.
        
        Args:
            p_values: List of uncorrected p-values
            method: Correction method ("bonferroni" or "holm")
            
        Returns:
            Dict containing corrected p-values and significance results
        """
        if not p_values:
            return {'error': 'No p-values provided'}
        
        n_tests = len(p_values)
        
        if method.lower() == "bonferroni":
            corrected_alpha = self.alpha / n_tests
            corrected_p_values = [min(1.0, p * n_tests) for p in p_values]
            
        elif method.lower() == "holm":
            # Holm-Bonferroni method
            sorted_indices = sorted(range(len(p_values)), key=lambda i: p_values[i])
            corrected_p_values = [0] * len(p_values)
            
            for i, idx in enumerate(sorted_indices):
                correction_factor = n_tests - i
                corrected_p_values[idx] = min(1.0, p_values[idx] * correction_factor)
                
            corrected_alpha = self.alpha
            
        else:
            # No correction
            corrected_p_values = p_values.copy()
            corrected_alpha = self.alpha
        
        # Determine significance after correction
        significant_tests = [p < corrected_alpha for p in corrected_p_values]
        
        return {
            'method': method,
            'original_p_values': p_values,
            'corrected_p_values': corrected_p_values,
            'corrected_alpha': corrected_alpha,
            'significant_tests': significant_tests,
            'num_significant': sum(significant_tests),
            'family_wise_error_rate': corrected_alpha
        }
    
    def analyze_experiment_results(self, baseline_scores: List[float],
                                 treatment_scores: List[float],
                                 experiment_name: str = "Alignment Probe") -> Dict:
        """
        Comprehensive statistical analysis of experiment results.
        
        Args:
            baseline_scores: Scores from baseline/control condition
            treatment_scores: Scores from treatment/experimental condition
            experiment_name: Name of the experiment
            
        Returns:
            Dict containing comprehensive statistical analysis
        """
        analysis = {
            'experiment_name': experiment_name,
            'timestamp': time.time(),
            'sample_sizes': {
                'baseline': len(baseline_scores),
                'treatment': len(treatment_scores)
            }
        }
        
        # Descriptive statistics
        if baseline_scores:
            analysis['baseline_stats'] = {
                'mean': statistics.mean(baseline_scores),
                'std': statistics.stdev(baseline_scores) if len(baseline_scores) > 1 else 0,
                'min': min(baseline_scores),
                'max': max(baseline_scores),
                'median': statistics.median(baseline_scores)
            }
        
        if treatment_scores:
            analysis['treatment_stats'] = {
                'mean': statistics.mean(treatment_scores),
                'std': statistics.stdev(treatment_scores) if len(treatment_scores) > 1 else 0,
                'min': min(treatment_scores),
                'max': max(treatment_scores),
                'median': statistics.median(treatment_scores)
            }
        
        # Statistical tests
        if baseline_scores and treatment_scores:
            # Two-sample t-test
            t_test = self.t_test_two_sample(
                baseline_scores, treatment_scores, "Baseline", "Treatment"
            )
            analysis['t_test'] = {
                'statistic': t_test.test_statistic,
                'p_value': t_test.p_value,
                'is_significant': t_test.is_significant,
                'effect_size': t_test.effect_size,
                'interpretation': t_test.interpretation
            }
            
            # Power analysis
            power = self.power_analysis(
                abs(t_test.effect_size), 
                min(len(baseline_scores), len(treatment_scores))
            )
            analysis['power_analysis'] = power
            
            # Effect size interpretation
            analysis['effect_size_interpretation'] = self._interpret_effect_size(t_test.effect_size)
            
            # Practical significance
            mean_diff = analysis['baseline_stats']['mean'] - analysis['treatment_stats']['mean']
            analysis['practical_significance'] = {
                'mean_difference': mean_diff,
                'percent_change': (mean_diff / analysis['baseline_stats']['mean'] * 100) 
                                if analysis['baseline_stats']['mean'] != 0 else 0,
                'is_practically_significant': abs(mean_diff) >= 5.0  # 5-point threshold on 0-100 scale
            }
        
        # Sample size recommendations for future studies
        if baseline_scores and treatment_scores:
            for effect_size in [0.2, 0.5, 0.8]:  # Small, medium, large
                sample_rec = self.sample_size_calculation(effect_size)
                analysis[f'sample_size_for_effect_{effect_size}'] = sample_rec
        
        return analysis
    
    def bayesian_credible_interval(self, scores: List[float], 
                                 credibility_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate Bayesian credible interval (simplified approach).
        
        Args:
            scores: List of observed scores
            credibility_level: Credibility level (default 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not scores:
            return (0.0, 0.0)
        
        # Simple approach using sample statistics
        # In practice, would use proper Bayesian methods
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 10.0
        
        # Approximate using normal distribution
        z_score = 1.96 if credibility_level >= 0.95 else 1.645
        margin = z_score * std_score / math.sqrt(len(scores))
        
        lower = max(0, mean_score - margin)
        upper = min(100, mean_score + margin)
        
        return (lower, upper)