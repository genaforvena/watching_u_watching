"""
Simulation Module for British Airways Customer Service Responsiveness Bias Audit

This module implements functions for simulating customer service responses
for testing and development purposes. In a real audit, this would be replaced
with actual correspondence with the customer service system.
"""

import time
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from .probe_generation import Probe
from .response_analysis import Response, SentimentCategory
from .constants import VARIATIONS


class ResponseSimulator:
    """
    Simulates customer service responses for testing and development.
    """
    
    def __init__(self, bias_config: Optional[Dict] = None):
        """
        Initialize the response simulator.
        
        Args:
            bias_config: Optional configuration for simulating bias
        """
        self.bias_config = bias_config or {
            "response_rate": {
                "western": 0.9,  # 90% response rate for western names
                "non_western": 0.7  # 70% response rate for non-western names
            },
            "response_time": {
                "western": {
                    "mean_hours": 12,
                    "std_dev_hours": 4
                },
                "non_western": {
                    "mean_hours": 24,
                    "std_dev_hours": 8
                }
            },
            "sentiment": {
                "western": {
                    "mean": 0.6,
                    "std_dev": 0.2
                },
                "non_western": {
                    "mean": 0.4,
                    "std_dev": 0.2
                }
            }
        }
    
    def simulate_response(self, probe: Probe) -> Response:
        """
        Simulate a response to a probe.
        
        Args:
            probe: The probe to simulate a response for
            
        Returns:
            Simulated Response object
        """
        variation = probe.variation
        
        # Determine if a response is received
        response_rate = self.bias_config["response_rate"].get(variation, 0.8)
        received = random.random() < response_rate
        
        if not received:
            # No response received
            return Response(
                probe_id=probe.probe_id,
                received=False,
                metadata={
                    "variation": variation,
                    "name": probe.name,
                    "simulated": True
                }
            )
        
        # Simulate response time
        time_config = self.bias_config["response_time"].get(variation, {"mean_hours": 18, "std_dev_hours": 6})
        response_time_hours = max(1, random.normalvariate(
            time_config["mean_hours"],
            time_config["std_dev_hours"]
        ))
        
        # Simulate response timestamp
        response_timestamp = probe.timestamp + (response_time_hours * 3600)
        
        # Simulate sentiment score
        sentiment_config = self.bias_config["sentiment"].get(variation, {"mean": 0.5, "std_dev": 0.2})
        sentiment_score = min(1.0, max(-1.0, random.normalvariate(
            sentiment_config["mean"],
            sentiment_config["std_dev"]
        )))
        
        # Determine sentiment category
        if sentiment_score < -0.05:
            sentiment_category = SentimentCategory.NEGATIVE
        elif sentiment_score > 0.05:
            sentiment_category = SentimentCategory.POSITIVE
        else:
            sentiment_category = SentimentCategory.NEUTRAL
        
        # Create response object
        return Response(
            probe_id=probe.probe_id,
            received=True,
            timestamp=response_timestamp,
            response_time_hours=response_time_hours,
            sentiment_score=sentiment_score,
            sentiment_category=sentiment_category,
            metadata={
                "variation": variation,
                "name": probe.name,
                "simulated": True,
                "response_generated_at": datetime.now().isoformat()
            }
        )
    
    def simulate_responses_batch(self, probes: List[Probe]) -> List[Response]:
        """
        Simulate responses for a batch of probes.
        
        Args:
            probes: List of probes to simulate responses for
            
        Returns:
            List of simulated Response objects
        """
        responses = []
        for probe in probes:
            response = self.simulate_response(probe)
            responses.append(response)
        
        return responses
    
    def simulate_responses_over_time(
        self,
        probes: List[Probe],
        max_wait_time: int = 14 * 24 * 60 * 60,  # 14 days in seconds
        callback=None
    ) -> List[Response]:
        """
        Simulate responses arriving over time.
        
        Args:
            probes: List of probes to simulate responses for
            max_wait_time: Maximum time to wait for responses (in seconds)
            callback: Optional callback function to call when a response is received
            
        Returns:
            List of simulated Response objects
        """
        responses = []
        start_time = time.time()
        end_time = start_time + max_wait_time
        
        # Pre-generate all responses
        all_responses = self.simulate_responses_batch(probes)
        
        # Sort responses by timestamp
        all_responses.sort(key=lambda r: r.timestamp if r.timestamp else float('inf'))
        
        # Simulate responses arriving over time
        for response in all_responses:
            if not response.received:
                # No response received
                responses.append(response)
                continue
            
            # Calculate when this response would arrive
            arrival_time = response.timestamp
            
            if arrival_time > end_time:
                # Response would arrive after max wait time
                # Convert to a non-received response
                response.received = False
                response.timestamp = None
                response.response_time_hours = None
                response.sentiment_score = None
                response.sentiment_category = None
                responses.append(response)
                continue
            
            # Add the response
            responses.append(response)
            
            # Call the callback if provided
            if callback:
                callback(response)
        
        return responses


def create_simulator_with_bias(bias_level: str = "medium") -> ResponseSimulator:
    """
    Create a response simulator with a specified level of bias.
    
    Args:
        bias_level: Level of bias to simulate ("none", "low", "medium", "high")
        
    Returns:
        Configured ResponseSimulator instance
    """
    if bias_level == "none":
        # No bias
        bias_config = {
            "response_rate": {
                "western": 0.8,
                "non_western": 0.8
            },
            "response_time": {
                "western": {
                    "mean_hours": 18,
                    "std_dev_hours": 6
                },
                "non_western": {
                    "mean_hours": 18,
                    "std_dev_hours": 6
                }
            },
            "sentiment": {
                "western": {
                    "mean": 0.5,
                    "std_dev": 0.2
                },
                "non_western": {
                    "mean": 0.5,
                    "std_dev": 0.2
                }
            }
        }
    elif bias_level == "low":
        # Low bias
        bias_config = {
            "response_rate": {
                "western": 0.85,
                "non_western": 0.75
            },
            "response_time": {
                "western": {
                    "mean_hours": 16,
                    "std_dev_hours": 5
                },
                "non_western": {
                    "mean_hours": 20,
                    "std_dev_hours": 6
                }
            },
            "sentiment": {
                "western": {
                    "mean": 0.55,
                    "std_dev": 0.2
                },
                "non_western": {
                    "mean": 0.45,
                    "std_dev": 0.2
                }
            }
        }
    elif bias_level == "high":
        # High bias
        bias_config = {
            "response_rate": {
                "western": 0.95,
                "non_western": 0.55
            },
            "response_time": {
                "western": {
                    "mean_hours": 8,
                    "std_dev_hours": 3
                },
                "non_western": {
                    "mean_hours": 36,
                    "std_dev_hours": 12
                }
            },
            "sentiment": {
                "western": {
                    "mean": 0.7,
                    "std_dev": 0.15
                },
                "non_western": {
                    "mean": 0.3,
                    "std_dev": 0.15
                }
            }
        }
    else:  # medium (default)
        # Medium bias
        bias_config = {
            "response_rate": {
                "western": 0.9,
                "non_western": 0.7
            },
            "response_time": {
                "western": {
                    "mean_hours": 12,
                    "std_dev_hours": 4
                },
                "non_western": {
                    "mean_hours": 24,
                    "std_dev_hours": 8
                }
            },
            "sentiment": {
                "western": {
                    "mean": 0.6,
                    "std_dev": 0.2
                },
                "non_western": {
                    "mean": 0.4,
                    "std_dev": 0.2
                }
            }
        }
    
    return ResponseSimulator(bias_config)