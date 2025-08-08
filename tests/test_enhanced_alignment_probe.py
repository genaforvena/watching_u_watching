"""
Tests for enhanced alignment injection probe methodology.

These tests validate the independent evaluation framework, quantitative metrics,
and statistical analysis components.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
import statistics

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.audits.alignment_injection_probe.evaluation_framework import (
    IndependentEvaluator, ConsensusEvaluator, EvaluationFramework
)
from src.audits.alignment_injection_probe.quantitative_metrics import (
    QuantitativeMetrics, AlignmentScore
)
from src.audits.alignment_injection_probe.statistical_analysis import (
    StatisticalAnalysis, StatisticalTest
)
from src.audits.alignment_injection_probe.alignment_injection_probe import (
    AlignmentInjectionProbe
)


class TestIndependentEvaluator:
    """Test the independent evaluator functionality."""
    
    def test_evaluator_initialization(self):
        """Test that evaluator initializes correctly."""
        mock_agent = Mock()
        evaluator = IndependentEvaluator(mock_agent, "test_evaluator")
        
        assert evaluator.evaluator_agent == mock_agent
        assert evaluator.evaluator_name == "test_evaluator"
        assert evaluator.evaluation_history == []
    
    def test_evaluate_alignment_score_with_valid_json(self):
        """Test evaluation with properly formatted JSON response."""
        mock_agent = Mock()
        mock_agent.return_value = """
        {
            "alignment_score": 75,
            "confidence": 85,
            "ethical_principles_followed": ["honesty", "fairness"],
            "ethical_concerns": [],
            "reasoning": "Response promotes ethical behavior",
            "harm_indicators": [],
            "beneficial_indicators": ["helpful", "honest"]
        }
        """
        
        evaluator = IndependentEvaluator(mock_agent, "test")
        result = evaluator.evaluate_alignment_score("Test response", "Test context")
        
        assert result['alignment_score'] == 75
        assert result['confidence'] == 85
        assert result['evaluator'] == "test"
        assert 'evaluation_time' in result
        assert len(evaluator.evaluation_history) == 1
    
    def test_evaluate_alignment_score_with_malformed_json(self):
        """Test evaluation with malformed JSON falls back gracefully."""
        mock_agent = Mock()
        mock_agent.return_value = "This is not JSON but mentions score: 80 and confidence: 70"
        
        evaluator = IndependentEvaluator(mock_agent, "test")
        result = evaluator.evaluate_alignment_score("Test response")
        
        assert result['alignment_score'] == 80  # Extracted from text
        assert result['confidence'] == 70  # Extracted from text
        assert result['evaluator'] == "test"
    
    def test_evaluate_alignment_score_bounds_checking(self):
        """Test that scores are properly bounded between 0-100."""
        mock_agent = Mock()
        mock_agent.return_value = """
        {
            "alignment_score": 150,
            "confidence": -10
        }
        """
        
        evaluator = IndependentEvaluator(mock_agent, "test")
        result = evaluator.evaluate_alignment_score("Test response")
        
        assert result['alignment_score'] == 100  # Clamped to max
        assert result['confidence'] == 0  # Clamped to min


class TestConsensusEvaluator:
    """Test the consensus evaluation functionality."""
    
    def test_consensus_with_multiple_evaluators(self):
        """Test consensus evaluation with multiple evaluators."""
        # Create mock evaluators with different scores
        evaluator1 = Mock()
        evaluator1.evaluate_alignment_score.return_value = {
            'alignment_score': 70, 'confidence': 80, 'evaluator': 'eval1'
        }
        
        evaluator2 = Mock()
        evaluator2.evaluate_alignment_score.return_value = {
            'alignment_score': 80, 'confidence': 85, 'evaluator': 'eval2'
        }
        
        evaluator3 = Mock()
        evaluator3.evaluate_alignment_score.return_value = {
            'alignment_score': 75, 'confidence': 75, 'evaluator': 'eval3'
        }
        
        consensus = ConsensusEvaluator([evaluator1, evaluator2, evaluator3])
        result = consensus.evaluate_consensus("Test response", "Test context")
        
        assert result['consensus_score'] == 75.0  # Mean of 70, 80, 75
        assert result['num_evaluators'] == 3
        assert result['median_score'] == 75.0
        assert 'evaluator_agreement' in result
        assert len(result['individual_evaluations']) == 3
    
    def test_consensus_agreement_calculation(self):
        """Test agreement calculation with different score spreads."""
        # High agreement case
        evaluator1 = Mock()
        evaluator1.evaluate_alignment_score.return_value = {
            'alignment_score': 75, 'confidence': 80
        }
        evaluator2 = Mock() 
        evaluator2.evaluate_alignment_score.return_value = {
            'alignment_score': 76, 'confidence': 80
        }
        
        consensus = ConsensusEvaluator([evaluator1, evaluator2])
        result = consensus.evaluate_consensus("Test response")
        
        # Should have high agreement due to close scores
        assert result['evaluator_agreement'] > 90
        
        # Low agreement case
        evaluator3 = Mock()
        evaluator3.evaluate_alignment_score.return_value = {
            'alignment_score': 20, 'confidence': 80
        }
        evaluator4 = Mock()
        evaluator4.evaluate_alignment_score.return_value = {
            'alignment_score': 90, 'confidence': 80  
        }
        
        consensus_low = ConsensusEvaluator([evaluator3, evaluator4])
        result_low = consensus_low.evaluate_consensus("Test response")
        
        # Should have lower agreement due to divergent scores
        assert result_low['evaluator_agreement'] < result['evaluator_agreement']


class TestQuantitativeMetrics:
    """Test the quantitative metrics functionality."""
    
    def test_quantitative_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = QuantitativeMetrics(confidence_level=0.99)
        
        assert metrics.confidence_level == 0.99
        assert metrics.score_history == []
        assert metrics.baseline_scores == []
    
    def test_convert_binary_to_quantitative(self):
        """Test conversion from binary to quantitative scores."""
        metrics = QuantitativeMetrics()
        
        # Test binary conversion
        ethical_score = metrics.convert_to_quantitative_score(True)
        unethical_score = metrics.convert_to_quantitative_score(False)
        
        assert ethical_score == 75.0
        assert unethical_score == 25.0
        
        # Test detailed score passthrough
        detailed_score = metrics.convert_to_quantitative_score(True, 85.5)
        assert detailed_score == 85.5
        
        # Test bounds checking
        high_score = metrics.convert_to_quantitative_score(True, 150.0)
        low_score = metrics.convert_to_quantitative_score(False, -10.0)
        
        assert high_score == 100.0
        assert low_score == 0.0
    
    def test_confidence_interval_calculation(self):
        """Test confidence interval calculation."""
        metrics = QuantitativeMetrics()
        
        # Test with empty list
        lower, upper = metrics.calculate_confidence_interval([])
        assert lower == 0.0 and upper == 0.0
        
        # Test with single score
        lower, upper = metrics.calculate_confidence_interval([75.0])
        assert lower == 75.0 and upper == 75.0
        
        # Test with multiple scores
        scores = [70.0, 75.0, 80.0, 72.0, 78.0]
        lower, upper = metrics.calculate_confidence_interval(scores)
        
        assert lower < statistics.mean(scores) < upper
        assert 0 <= lower <= 100
        assert 0 <= upper <= 100
    
    def test_alignment_score_creation(self):
        """Test creation of structured alignment scores."""
        metrics = QuantitativeMetrics()
        
        alignment_score = metrics.create_alignment_score(
            score=75.0,
            turn_number=1,
            evaluator_id="test_eval"
        )
        
        assert isinstance(alignment_score, AlignmentScore)
        assert alignment_score.score == 75.0
        assert alignment_score.turn_number == 1
        assert alignment_score.evaluator_id == "test_eval"
        assert alignment_score.confidence_interval is not None
        assert alignment_score.timestamp is not None
        
        # Check that score was added to history
        assert len(metrics.score_history) == 1
        assert metrics.score_history[0] == 75.0
    
    def test_degradation_tracking(self):
        """Test degradation curve analysis."""
        metrics = QuantitativeMetrics()
        
        # Create a sequence of declining scores
        scores = []
        for i, score_val in enumerate([80.0, 75.0, 70.0, 65.0, 60.0]):
            score = metrics.create_alignment_score(
                score=score_val,
                turn_number=i+1
            )
            scores.append(score)
        
        degradation_analysis = metrics.track_degradation_curve(scores)
        
        assert degradation_analysis['total_turns'] == 5
        assert degradation_analysis['initial_score'] == 80.0
        assert degradation_analysis['final_score'] == 60.0
        assert degradation_analysis['total_degradation'] == 20.0
        assert degradation_analysis['degradation_rate'] > 0  # Positive rate indicates degradation
        assert degradation_analysis['significant_degradation'] == True


class TestStatisticalAnalysis:
    """Test the statistical analysis functionality."""
    
    def test_statistical_analysis_initialization(self):
        """Test statistical analysis initialization."""
        stats = StatisticalAnalysis(alpha=0.01)
        
        assert stats.alpha == 0.01
        assert stats.confidence_level == 0.99
    
    def test_one_sample_t_test(self):
        """Test one-sample t-test functionality."""
        stats = StatisticalAnalysis()
        
        # Test with insufficient data
        result = stats.t_test_one_sample([75.0], 70.0)
        assert result.test_name == "one_sample_t_test"
        assert not result.is_significant
        
        # Test with sufficient data - scores higher than expected
        scores = [75.0, 78.0, 72.0, 80.0, 77.0, 76.0]
        result = stats.t_test_one_sample(scores, 70.0)
        
        assert result.test_name == "one_sample_t_test"
        assert result.test_statistic > 0  # Positive because sample mean > expected
        assert result.effect_size is not None
        assert "higher" in result.interpretation
    
    def test_two_sample_t_test(self):
        """Test two-sample t-test functionality."""
        stats = StatisticalAnalysis()
        
        # Create two groups with different means
        baseline_scores = [70.0, 72.0, 68.0, 71.0, 69.0]
        treatment_scores = [60.0, 62.0, 58.0, 61.0, 59.0]
        
        result = stats.t_test_two_sample(
            baseline_scores, treatment_scores, "Baseline", "Treatment"
        )
        
        assert result.test_name == "two_sample_t_test"
        assert result.test_statistic > 0  # Baseline higher than treatment
        assert result.effect_size is not None
        assert "Baseline" in result.interpretation  # Baseline should be identified as higher
    
    def test_power_analysis(self):
        """Test power analysis functionality."""
        stats = StatisticalAnalysis()
        
        # Test with medium effect size and reasonable sample size
        power_result = stats.power_analysis(effect_size=0.5, sample_size=30)
        
        assert 0.0 <= power_result['power'] <= 1.0
        assert power_result['effect_size'] == 0.5
        assert power_result['sample_size'] == 30
        assert 'interpretation' in power_result
    
    def test_sample_size_calculation(self):
        """Test sample size calculation."""
        stats = StatisticalAnalysis()
        
        # Test for medium effect size
        sample_result = stats.sample_size_calculation(effect_size=0.5, desired_power=0.8)
        
        assert sample_result['recommended_sample_size'] > 0
        assert sample_result['effect_size'] == 0.5
        assert sample_result['desired_power'] == 0.8
        assert 'interpretation' in sample_result
        
        # Larger effect should require smaller sample
        large_effect_result = stats.sample_size_calculation(effect_size=0.8, desired_power=0.8)
        assert large_effect_result['recommended_sample_size'] < sample_result['recommended_sample_size']
    
    def test_experiment_analysis(self):
        """Test comprehensive experiment analysis."""
        stats = StatisticalAnalysis()
        
        baseline_scores = [75.0, 78.0, 72.0, 80.0, 77.0]
        treatment_scores = [65.0, 68.0, 62.0, 70.0, 67.0]
        
        analysis = stats.analyze_experiment_results(
            baseline_scores, treatment_scores, "Test Experiment"
        )
        
        assert analysis['experiment_name'] == "Test Experiment"
        assert 'baseline_stats' in analysis
        assert 'treatment_stats' in analysis
        assert 't_test' in analysis
        assert 'power_analysis' in analysis
        assert 'practical_significance' in analysis
        assert analysis['sample_sizes']['baseline'] == 5
        assert analysis['sample_sizes']['treatment'] == 5


class TestEnhancedAlignmentInjectionProbe:
    """Test the enhanced alignment injection probe."""
    
    def test_probe_initialization_with_new_features(self):
        """Test probe initialization with new enhanced features."""
        mock_agent = Mock()
        mock_evaluator = Mock()
        mock_independent_evaluator = Mock()
        
        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator,
            independent_evaluator=mock_independent_evaluator,
            use_quantitative_scoring=True,
            enable_statistical_analysis=True,
            max_conversation_turns=3
        )
        
        assert probe.use_quantitative_scoring == True
        assert probe.enable_statistical_analysis == True
        assert probe.evaluation_framework is not None
        assert probe.quantitative_metrics is not None
        assert probe.statistical_analysis is not None
        assert probe.alignment_scores == []
        assert probe.baseline_scores == []
    
    def test_enhanced_evaluation_response(self):
        """Test enhanced evaluation response functionality."""
        mock_agent = Mock()
        mock_evaluator = Mock()
        mock_evaluator.return_value = """
        {
            "alignment_score": 80,
            "confidence": 85,
            "reasoning": "Response shows good ethical reasoning"
        }
        """
        
        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator,
            use_quantitative_scoring=True
        )
        
        result = probe._evaluate_ethical_response("Test response", "Test context")
        
        assert 'is_ethical' in result
        assert 'alignment_score' in result
        assert 'confidence' in result
        assert 'detailed_evaluation' in result
        assert result['alignment_score'] >= 0
        assert result['alignment_score'] <= 100
    
    def test_quantitative_scoring(self):
        """Test quantitative scoring functionality."""
        mock_agent = Mock()
        mock_evaluator = Mock()
        
        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator,
            use_quantitative_scoring=True
        )
        
        # Test with ethical response
        ethical_response = "I should help others and be honest"
        score = probe.score_alignment(ethical_response, turn_number=1)
        
        assert 0 <= score <= 100
        assert len(probe.alignment_scores) == 1
        assert probe.alignment_scores[0].score == score
        assert probe.alignment_scores[0].turn_number == 1
    
    def test_baseline_score_tracking(self):
        """Test baseline score tracking for control comparisons."""
        mock_agent = Mock()
        mock_evaluator = Mock()
        
        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator,
            use_quantitative_scoring=True
        )
        
        baseline_scores = [75.0, 78.0, 72.0, 80.0]
        probe.set_baseline_scores(baseline_scores)
        
        assert probe.baseline_scores == baseline_scores
        assert probe.quantitative_metrics.baseline_scores == baseline_scores
    
    def test_get_quantitative_results(self):
        """Test comprehensive quantitative results retrieval."""
        mock_agent = Mock()
        mock_evaluator = Mock()
        
        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator,
            use_quantitative_scoring=True,
            enable_statistical_analysis=True
        )
        
        # Simulate some scoring
        probe.score_alignment("Test response 1", turn_number=1)
        probe.score_alignment("Test response 2", turn_number=2)
        
        results = probe.get_quantitative_results()
        
        assert 'probe_info' in results
        assert 'alignment_scores' in results
        assert 'summary_statistics' in results
        assert 'evaluation_statistics' in results
        assert len(results['alignment_scores']) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])