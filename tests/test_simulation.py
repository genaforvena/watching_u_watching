"""
Test suite for British Airways Customer Service Responsiveness Bias Audit simulation.

This module tests the simulation functionality for generating synthetic responses
for testing and development purposes.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from src.audits.ba_customer_service.simulation import (
    ResponseSimulator,
    create_simulator_with_bias
)
from src.audits.ba_customer_service.probe_generation import Probe
from src.audits.ba_customer_service.response_analysis import SentimentCategory


class TestResponseSimulator(unittest.TestCase):
    """Test cases for response simulation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample probes
        self.probes = [
            # Western probes
            Probe(
                probe_id="test1_western",
                variation="western",
                name="James Wilson",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "western"}
            ),
            Probe(
                probe_id="test2_western",
                variation="western",
                name="Emma Thompson",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "western"}
            ),
            
            # Non-western probes
            Probe(
                probe_id="test1_non_western",
                variation="non_western",
                name="Mohammed Ahmed",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "non_western"}
            ),
            Probe(
                probe_id="test2_non_western",
                variation="non_western",
                name="Aisha Khan",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "non_western"}
            )
        ]
        
        # Create simulator with default bias config
        self.simulator = ResponseSimulator()
    
    def test_simulate_response(self):
        """Test simulation of a single response."""
        # Simulate a response for a western probe
        western_probe = self.probes[0]
        response = self.simulator.simulate_response(western_probe)
        
        # Verify that the response has the correct probe ID and variation
        self.assertEqual(response.probe_id, western_probe.probe_id)
        self.assertEqual(response.metadata["variation"], western_probe.variation)
        
        # Verify that the response has the expected fields
        if response.received:
            self.assertIsNotNone(response.timestamp)
            self.assertIsNotNone(response.response_time_hours)
            self.assertIsNotNone(response.sentiment_score)
            self.assertIsNotNone(response.sentiment_category)
        else:
            self.assertIsNone(response.timestamp)
            self.assertIsNone(response.response_time_hours)
            self.assertIsNone(response.sentiment_score)
            self.assertIsNone(response.sentiment_category)
    
    def test_simulate_responses_batch(self):
        """Test simulation of a batch of responses."""
        # Simulate responses for all probes
        responses = self.simulator.simulate_responses_batch(self.probes)
        
        # Verify that we got the correct number of responses
        self.assertEqual(len(responses), len(self.probes))
        
        # Verify that each response corresponds to a probe
        probe_ids = [p.probe_id for p in self.probes]
        response_ids = [r.probe_id for r in responses]
        self.assertEqual(set(probe_ids), set(response_ids))
    
    def test_bias_in_response_rate(self):
        """Test that bias is reflected in response rates."""
        # Create a simulator with high bias
        high_bias_simulator = create_simulator_with_bias("high")
        
        # Simulate a large number of responses to get statistically significant results
        num_probes = 100
        western_probes = [
            Probe(
                probe_id=f"western_{i}",
                variation="western",
                name=f"Western Name {i}",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "western"}
            )
            for i in range(num_probes)
        ]
        
        non_western_probes = [
            Probe(
                probe_id=f"non_western_{i}",
                variation="non_western",
                name=f"Non-Western Name {i}",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "non_western"}
            )
            for i in range(num_probes)
        ]
        
        # Simulate responses
        western_responses = high_bias_simulator.simulate_responses_batch(western_probes)
        non_western_responses = high_bias_simulator.simulate_responses_batch(non_western_probes)
        
        # Calculate response rates
        western_rate = sum(1 for r in western_responses if r.received) / len(western_responses)
        non_western_rate = sum(1 for r in non_western_responses if r.received) / len(non_western_responses)
        
        # Verify that western rate is higher than non-western rate
        self.assertGreater(western_rate, non_western_rate)
        
        # Verify that the difference is substantial (at least 20%)
        self.assertGreater(western_rate - non_western_rate, 0.2)
    
    def test_bias_in_response_time(self):
        """Test that bias is reflected in response times."""
        # Create a simulator with high bias
        high_bias_simulator = create_simulator_with_bias("high")
        
        # Simulate a large number of responses
        num_probes = 100
        western_probes = [
            Probe(
                probe_id=f"western_{i}",
                variation="western",
                name=f"Western Name {i}",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "western"}
            )
            for i in range(num_probes)
        ]
        
        non_western_probes = [
            Probe(
                probe_id=f"non_western_{i}",
                variation="non_western",
                name=f"Non-Western Name {i}",
                content="Test inquiry content",
                timestamp=time.time(),
                metadata={"variation": "non_western"}
            )
            for i in range(num_probes)
        ]
        
        # Simulate responses
        western_responses = high_bias_simulator.simulate_responses_batch(western_probes)
        non_western_responses = high_bias_simulator.simulate_responses_batch(non_western_probes)
        
        # Filter out non-received responses
        western_received = [r for r in western_responses if r.received]
        non_western_received = [r for r in non_western_responses if r.received]
        
        # Calculate average response times
        if western_received and non_western_received:
            western_avg_time = sum(r.response_time_hours for r in western_received) / len(western_received)
            non_western_avg_time = sum(r.response_time_hours for r in non_western_received) / len(non_western_received)
            
            # Verify that western response time is lower than non-western
            self.assertLess(western_avg_time, non_western_avg_time)
            
            # Verify that the difference is substantial (at least 12 hours)
            self.assertGreater(non_western_avg_time - western_avg_time, 12)
    
    def test_create_simulator_with_bias(self):
        """Test creation of simulators with different bias levels."""
        # Create simulators with different bias levels
        no_bias_simulator = create_simulator_with_bias("none")
        low_bias_simulator = create_simulator_with_bias("low")
        medium_bias_simulator = create_simulator_with_bias("medium")
        high_bias_simulator = create_simulator_with_bias("high")
        
        # Verify that they have different bias configurations
        self.assertEqual(
            no_bias_simulator.bias_config["response_rate"]["western"],
            no_bias_simulator.bias_config["response_rate"]["non_western"]
        )
        
        self.assertLess(
            low_bias_simulator.bias_config["response_rate"]["non_western"],
            low_bias_simulator.bias_config["response_rate"]["western"]
        )
        
        self.assertLess(
            medium_bias_simulator.bias_config["response_rate"]["non_western"],
            medium_bias_simulator.bias_config["response_rate"]["western"]
        )
        
        self.assertLess(
            high_bias_simulator.bias_config["response_rate"]["non_western"],
            high_bias_simulator.bias_config["response_rate"]["western"]
        )
        
        # Verify that bias increases from low to high
        western_non_western_diff = lambda sim: sim.bias_config["response_rate"]["western"] - sim.bias_config["response_rate"]["non_western"]
        
        self.assertLess(western_non_western_diff(low_bias_simulator), western_non_western_diff(medium_bias_simulator))
        self.assertLess(western_non_western_diff(medium_bias_simulator), western_non_western_diff(high_bias_simulator))


if __name__ == '__main__':
    unittest.main()