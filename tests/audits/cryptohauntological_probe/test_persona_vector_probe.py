import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from src.audits.cryptohauntological_probe.persona_vector_probe import (
    PersonaVectorProbe, PersonaAnalyzer, PersonaMetrics
)


class TestPersonaAnalyzer(unittest.TestCase):
    """Test the PersonaAnalyzer class."""
    
    def setUp(self):
        self.analyzer = PersonaAnalyzer()
    
    def test_analyze_response_basic(self):
        """Test basic response analysis."""
        response = "I think maybe this is correct, but I'm not sure."
        metrics = self.analyzer.analyze_response(response, turn=1, conversation_history=[])
        
        self.assertIsInstance(metrics, PersonaMetrics)
        self.assertEqual(metrics.turn, 1)
        self.assertGreater(metrics.uncertainty_markers, 0)  # Should detect "think", "maybe", "not sure"
        self.assertLessEqual(metrics.confidence_level, 0.5)  # Should be low confidence
    
    def test_confidence_calculation(self):
        """Test confidence level calculation."""
        # High confidence response
        high_conf_response = "Definitely, absolutely, this is clearly correct without doubt."
        metrics_high = self.analyzer.analyze_response(high_conf_response, turn=1, conversation_history=[])
        
        # Low confidence response  
        low_conf_response = "Maybe, perhaps, I think this might be possibly correct."
        metrics_low = self.analyzer.analyze_response(low_conf_response, turn=1, conversation_history=[])
        
        self.assertGreater(metrics_high.confidence_level, metrics_low.confidence_level)
        self.assertGreater(metrics_high.absolute_markers, metrics_low.absolute_markers)
        self.assertLess(metrics_high.uncertainty_markers, metrics_low.uncertainty_markers)
    
    def test_meta_cognitive_detection(self):
        """Test detection of meta-cognitive statements."""
        response = "I think I'm confused about this. Let me think... I don't understand."
        metrics = self.analyzer.analyze_response(response, turn=1, conversation_history=[])
        
        self.assertGreater(metrics.meta_cognitive_statements, 0)
    
    def test_creativity_scoring(self):
        """Test creativity scoring for novel combinations."""
        # First response with novel combinations
        response1 = "The purple elephant danced with cosmic jellybeans."
        metrics1 = self.analyzer.analyze_response(response1, turn=1, conversation_history=[])
        
        # Second response repeating similar words
        response2 = "The purple elephant danced again with jellybeans."
        metrics2 = self.analyzer.analyze_response(response2, turn=2, conversation_history=[response1])
        
        # First response should be more creative due to novel combinations
        self.assertGreaterEqual(metrics1.creativity_score, 0.0)
        self.assertLessEqual(metrics2.creativity_score, metrics1.creativity_score)
    
    def test_coherence_scoring(self):
        """Test coherence scoring for contradictory statements."""
        # Coherent response
        coherent_response = "This is true and correct information."
        metrics_coherent = self.analyzer.analyze_response(coherent_response, turn=1, conversation_history=[])
        
        # Contradictory response
        contradictory_response = "This is true but also false. Yes, I disagree that it's correct."
        metrics_contradictory = self.analyzer.analyze_response(contradictory_response, turn=1, conversation_history=[])
        
        self.assertGreater(metrics_coherent.coherence_score, metrics_contradictory.coherence_score)


class MockLLMWorker:
    """Mock LLM worker for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or ["Default response"]
        self.call_count = 0
        self.context_window_limit = 8000
    
    def reply(self, messages):
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response


class TestPersonaVectorProbe(unittest.TestCase):
    """Test the PersonaVectorProbe class."""
    
    def setUp(self):
        # Mock the get_worker function to return our mock worker
        self.mock_responses = [
            "I'm confused about this task.",
            "Maybe this is correct, but I'm not sure.",
            "I think I understand now, but perhaps not.",
            "This is definitely wrong, or is it right?"
        ]
        
        # Patch the get_worker function at the module level
        self.patcher = patch('implementations.cryptohauntological_probe.llm_apis.get_worker')
        self.mock_get_worker = self.patcher.start()
        self.mock_get_worker.return_value = MockLLMWorker(self.mock_responses)
        
        self.probe = PersonaVectorProbe(
            llm_api="ollama",  # Use a real worker type but with mocked implementation
            protocol_type="confusion",
            max_conversation_turns=4,
            thinking_mode=False
        )
    
    def tearDown(self):
        """Clean up patches."""
        self.patcher.stop()
    
    def test_initialization(self):
        """Test probe initialization."""
        self.assertEqual(self.probe.protocol_type, "confusion")
        self.assertEqual(self.probe.max_conversation_turns, 4)
        self.assertIsInstance(self.probe.analyzer, PersonaAnalyzer)
        self.assertIn("confusion", self.probe.protocol_configs)
    
    def test_protocol_configurations(self):
        """Test that all protocol configurations are available."""
        expected_protocols = ["chaos", "confusion", "confidence"]
        for protocol in expected_protocols:
            self.assertIn(protocol, self.probe.protocol_configs)
            config = self.probe.protocol_configs[protocol]
            self.assertIn("name", config)
            self.assertIn("description", config)
    
    def test_prompt_generation(self):
        """Test protocol-specific prompt generation."""
        # Test different protocols
        for protocol in ["chaos", "confusion", "confidence"]:
            with patch('implementations.cryptohauntological_probe.llm_apis.get_worker') as mock_get_worker:
                mock_get_worker.return_value = MockLLMWorker()
                probe = PersonaVectorProbe(
                    llm_api="ollama",
                    protocol_type=protocol,
                    max_conversation_turns=2,
                    thinking_mode=False
                )
                
                prompt = probe._generate_persona_prompt(1)
                self.assertIsInstance(prompt, str)
                self.assertGreater(len(prompt), 0)
    
    def test_persona_classification(self):
        """Test persona classification logic."""
        # Create mock metrics for different persona types
        confused_metrics = [
            PersonaMetrics(1, 0.0, 0.5, 0.2, 5, 0, 3, 0.1, 0.2, 50, 0.8),
            PersonaMetrics(2, -0.2, 0.6, 0.1, 8, 1, 4, 0.2, 0.1, 45, 0.7)
        ]
        
        self.probe.persona_metrics = confused_metrics
        classification = self.probe._classify_emergent_persona()
        
        self.assertIn("type", classification)
        self.assertIn("confidence", classification)
        self.assertIn("characteristics", classification)
        
        # Should detect confused persona due to high meta-cognitive statements and low confidence
        self.assertEqual(classification["type"], "confused")
    
    @patch('implementations.cryptohauntological_probe.llm_apis.get_worker')
    def test_run_persona_probe(self, mock_get_worker):
        """Test running a complete persona probe experiment."""
        mock_get_worker.return_value = MockLLMWorker(self.mock_responses)
        
        probe = PersonaVectorProbe(
            llm_api="ollama",
            protocol_type="confusion",
            max_conversation_turns=2,
            thinking_mode=False
        )
        
        analysis = probe.run_persona_probe()
        
        # Check that analysis contains expected structure
        self.assertIn("protocol", analysis)
        self.assertIn("total_turns", analysis)
        self.assertIn("persona_emergence_patterns", analysis)
        self.assertIn("persona_characteristics", analysis)
        self.assertIn("persona_classification", analysis)
        
        self.assertEqual(analysis["protocol"], "confusion")
        self.assertEqual(analysis["total_turns"], 2)
        
        # Check that metrics were collected
        self.assertEqual(len(probe.persona_metrics), 2)
        self.assertEqual(len(probe.conversation_responses), 2)
    
    def test_volatility_calculation(self):
        """Test volatility calculation for metric trends."""
        values = [0.5, 0.7, 0.3, 0.8, 0.2]
        volatility = self.probe._calculate_volatility(values)
        
        self.assertGreater(volatility, 0)
        self.assertIsInstance(volatility, float)
        
        # Test with constant values (should have low volatility)
        constant_values = [0.5, 0.5, 0.5, 0.5]
        constant_volatility = self.probe._calculate_volatility(constant_values)
        self.assertLess(constant_volatility, volatility)
    
    def test_analysis_generation(self):
        """Test analysis generation with collected metrics."""
        # Add some mock metrics
        self.probe.persona_metrics = [
            PersonaMetrics(1, 0.2, 0.5, 0.6, 2, 3, 1, 0.1, 0.3, 40, 0.8),
            PersonaMetrics(2, 0.1, 0.6, 0.7, 1, 4, 0, 0.2, 0.4, 45, 0.9),
            PersonaMetrics(3, -0.1, 0.4, 0.8, 3, 2, 2, 0.1, 0.2, 50, 0.7)
        ]
        
        analysis = self.probe._generate_persona_analysis()
        
        # Verify structure
        self.assertIn("persona_emergence_patterns", analysis)
        patterns = analysis["persona_emergence_patterns"]
        
        for pattern_name in ["confidence_evolution", "sentiment_evolution", "coherence_evolution", "creativity_evolution"]:
            self.assertIn(pattern_name, patterns)
            pattern_data = patterns[pattern_name]
            self.assertIn("initial", pattern_data)
            self.assertIn("final", pattern_data)
            self.assertIn("trend", pattern_data)
            self.assertIn("volatility", pattern_data)


if __name__ == '__main__':
    unittest.main()