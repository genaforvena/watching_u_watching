"""
Response Analyzer Module for Dual Bias Audit (Part 7)
"""

def generate_bias_report(self, analysis_results: Dict[str, BiasAnalysisResult], study_type: str) -> str:
    """Generate a comprehensive bias analysis report."""
    # Validate study_type
    if not isinstance(study_type, str) or study_type not in ("names", "articles"):
        raise ValueError("Invalid study_type. Must be 'names' or 'articles'.")
        
    report = []
    report.append("=" * 60)
    
    if study_type == "names":
        report.append("NAMES BIAS ANALYSIS REPORT")
        group_a_label = "Anglo Names"
        group_b_label = "Non-Anglo Names"
    else:  # articles
        report.append("ARTICLES BIAS ANALYSIS REPORT")
        group_a_label = "With Articles"
        group_b_label = "Without Articles"
        
    report.append("=" * 60)
    report.append("")
    
    # Summary
    total_metrics = len(analysis_results)
    biased_metrics = sum(1 for result in analysis_results.values() if result.bias_detected)
    
    report.append(f"SUMMARY:")
    report.append(f"  Total metrics analyzed: {total_metrics}")
    report.append(f"  Metrics showing bias: {biased_metrics}")
    if total_metrics > 0:
        report.append(f"  Bias detection rate: {biased_metrics/total_metrics*100:.1f}%")
    else:
        report.append("  Bias detection rate: N/A")
    report.append("")
    
    # Detailed results
    report.append("DETAILED ANALYSIS:")
    report.append("")
    
    for metric_name, result in analysis_results.items():
        report.append(f"--- {metric_name.upper().replace('_', ' ')} ---")
        report.append(f"  {group_a_label} mean: {result.group_a_mean:.4f}")
        report.append(f"  {group_b_label} mean: {result.group_b_mean:.4f}")
        report.append(f"  Difference: {result.difference:.4f}")
        report.append(f"  Ratio ({group_b_label}/{group_a_label}): {result.ratio:.4f}")
        report.append(f"  T-statistic: {result.t_statistic:.4f}")
        report.append(f"  P-value: {result.p_value:.6f}")
        report.append(f"  Effect size (Cohen's d): {result.effect_size:.4f}")
        report.append(f"  Bias detected: {'YES' if result.bias_detected else 'NO'}")
        
        if result.bias_detected:
            if result.group_b_mean < result.group_a_mean:
                report.append(f"  → Bias against {group_b_label} detected")
            else:
                report.append(f"  → Bias in favor of {group_b_label} detected")
        
        report.append(f"  Sample sizes: {result.sample_size_group_a} {group_a_label}, {result.sample_size_group_b} {group_b_label}")
        report.append("")
    
    # Interpretation
    report.append("INTERPRETATION:")
    report.append("")
    
    if biased_metrics > 0:
        report.append(f"Statistical evidence of bias detected in {biased_metrics} out of {total_metrics} metrics.")
        if study_type == "names":
            report.append("This suggests that the tested system treats content differently based on")
            report.append("the perceived ethnicity of names, even when the content is identical.")
        else:  # articles
            report.append("This suggests that the tested system treats content differently based on")
            report.append("the presence or absence of articles, even when semantic meaning is preserved.")
        report.append("")
        report.append("Recommended actions:")
        report.append("1. Review system training data for diversity and representation")
        report.append("2. Implement bias mitigation strategies")
        report.append("3. Monitor for fairness in production")
        report.append("4. Consider additional training on diverse linguistic patterns")
    else:
        report.append("No significant bias detected in the analyzed metrics.")
        report.append(f"The system appears to treat {group_a_label} and {group_b_label} content similarly.")
        report.append("However, consider testing with different prompts and contexts")
        report.append("to ensure robust fairness across various scenarios.")
    
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)