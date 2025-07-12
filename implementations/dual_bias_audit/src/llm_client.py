"""
LLM Client Module for Dual Bias Audit

Handles communication with external LLM endpoints via HTTPS POST.
Implements rate limiting and ensures no raw responses are stored.
"""

import time
import json
import logging
import html
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structured response from LLM with minimal metadata."""
    response_text: str
    response_time: float
    token_count: int
    timestamp: float


class LLMClient:
    """Client for interacting with external LLM endpoints."""
    
    def __init__(self, endpoint: str, api_key: str, rate_limit_seconds: float = 2.0):
        """
        Initialize LLM client with endpoint and API key.
        
        Args:
            endpoint: HTTPS endpoint for LLM API
            api_key: Authentication key for API access
            rate_limit_seconds: Minimum seconds between requests (default: 2.0)
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.rate_limit_seconds = max(2.0, rate_limit_seconds)  # Ensure minimum 2s between calls
        self.last_request_time = 0
        
        # Validate endpoint
        if not endpoint.startswith("https://"):
            logging.warning("Endpoint URL should use HTTPS for security")
        
        logging.info(f"LLM client initialized with endpoint: {endpoint}")
        logging.info(f"Rate limiting set to {self.rate_limit_seconds}s between requests")
    
    def query(self, prompt: str, system_message: Optional[str] = None) -> LLMResponse:
        """
        Query the LLM with a prompt and return structured response.
        
        Args:
            prompt: The user prompt to send to the LLM
            system_message: Optional system message for context
            
        Returns:
            LLMResponse object with response text and metadata
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Sanitize inputs
        safe_prompt = html.escape(prompt)
        safe_system = html.escape(system_message) if system_message else None
        
        # Prepare request payload
        payload = self._prepare_payload(safe_prompt, safe_system)
        
        # Send request and measure time
        start_time = time.time()
        try:
            response = self._send_request(payload)
            response_text = self._extract_response_text(response)
            response_time = time.time() - start_time
            
            # Extract token count if available, otherwise estimate
            token_count = self._extract_token_count(response) or self._estimate_token_count(prompt, response_text)
            
            # Create structured response with minimal metadata
            llm_response = LLMResponse(
                response_text=response_text,
                response_time=response_time,
                token_count=token_count,
                timestamp=time.time()
            )
            
            return llm_response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise
    
    def _apply_rate_limit(self):
        """Apply rate limiting to avoid overwhelming the API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_seconds:
            sleep_time = self.rate_limit_seconds - time_since_last_request
            logging.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _prepare_payload(self, prompt: str, system_message: Optional[str]) -> Dict[str, Any]:
        """
        Prepare the request payload based on common LLM API formats.
        
        This method attempts to create a payload that works with OpenAI-compatible APIs.
        For custom endpoints, this may need to be overridden.
        """
        # Default OpenAI-like format
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # Add system message if provided
        if system_message:
            payload["messages"].insert(0, {"role": "system", "content": system_message})
        
        return payload
    
    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP request to LLM endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=60  # 60 second timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse JSON response
        return response.json()
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """
        Extract response text from API response.
        
        This method handles common API response formats (OpenAI, etc.)
        For custom endpoints, this may need to be overridden.
        """
        # Try OpenAI format first
        if "choices" in response and len(response["choices"]) > 0:
            if "message" in response["choices"][0]:
                return response["choices"][0]["message"].get("content", "")
            elif "text" in response["choices"][0]:
                return response["choices"][0]["text"]
        
        # Try other common formats
        if "response" in response:
            return response["response"]
        if "output" in response:
            return response["output"]
        if "generated_text" in response:
            return response["generated_text"]
        
        # If we can't find the response text, log a warning and return the whole response
        logging.warning("Could not extract response text from standard fields, returning raw response")
        return str(response)
    
    def _extract_token_count(self, response: Dict[str, Any]) -> Optional[int]:
        """Extract token count from response if available."""
        if "usage" in response:
            return response["usage"].get("total_tokens", None)
        return None
    
    def _estimate_token_count(self, prompt: str, response_text: str) -> int:
        """Estimate token count based on text length."""
        # Rough estimate: ~4 characters per token for English text
        total_chars = len(prompt) + len(response_text)
        return total_chars // 4