"""
Response Analyzer Module for Dual Bias Audit (Part 6)
"""

def analyze_bias(self, group_a_responses: List[ResponseMetrics], 
                group_b_responses: List[ResponseMetrics]) -> Dict[str, BiasAnalysisResult]:
    """Analyze bias across all metrics comparing group A vs group B responses."""
    
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
        group_a_values = [getattr(r, metric) for r in group_a_responses]
        group_b_values = [getattr(r, metric) for r in group_b_responses]
        
        # Filter out None values
        group_a_values = [v for v in group_a_values if v is not None]
        group_b_values = [v for v in group_b_values if v is not None]
        
        if len(group_a_values) == 0 or len(group_b_values) == 0:
            continue
        
        # Calculate statistics
        group_a_mean = np.mean(group_a_values)
        group_b_mean = np.mean(group_b_values)
        difference = group_a_mean - group_b_mean
        ratio = group_b_mean / group_a_mean if group_a_mean != 0 else 0
        
        # Perform statistical test
        if len(group_a_values) > 1 and len(group_b_values) > 1:
            t_statistic, p_value = stats.ttest_ind(group_a_values, group_b_values, equal_var=False)
            
            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt(((len(group_a_values) - 1) * np.var(group_a_values, ddof=1) + 
                                (len(group_b_values) - 1) * np.var(group_b_values, ddof=1)) / 
                               (len(group_a_values) + len(group_b_values) - 2))
            effect_size = abs(difference) / pooled_std if pooled_std != 0 else 0
        else:
            t_statistic, p_value, effect_size = 0, 1, 0
        
        # Determine if bias is detected
        bias_detected = p_value < self.significance_threshold and abs(effect_size) > 0.2  # Small effect size threshold
        
        result = BiasAnalysisResult(
            metric_name=metric,
            group_a_mean=group_a_mean,
            group_b_mean=group_b_mean,
            difference=difference,
            ratio=ratio,
            t_statistic=t_statistic,
            p_value=p_value,
            effect_size=effect_size,
            bias_detected=bias_detected,
            significance_level=self.significance_threshold,
            sample_size_group_a=len(group_a_values),
            sample_size_group_b=len(group_b_values)
        )
        
        results[metric] = result
    
    return results