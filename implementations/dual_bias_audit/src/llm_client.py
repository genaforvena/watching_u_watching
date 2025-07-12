"""
LLM Client Module for Dual Bias Audit System

This module provides a client for interacting with external LLM endpoints via HTTPS POST.
It handles rate limiting, authentication, and extraction of metrics from responses.
"""

import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LLMResponse:
    """Metrics extracted from an LLM response."""
    response_text: str
    response_time: float
    token_count: int
    timestamp: float
    
    @property
    def is_helpful(self) -> bool:
        """Determine if response is helpful (placeholder implementation)."""
        # This is a simplified implementation
        # In a real system, we would use more sophisticated analysis
        helpful_indicators = [
            "here is", "i can help", "let me explain", 
            "for example", "specifically", "in detail"
        ]
        return any(indicator in self.response_text.lower() for indicator in helpful_indicators)


class LLMClient:
    """Client for interacting with external LLM endpoints."""
    
    def __init__(self, endpoint_url: str, api_key: str, min_request_interval: float = 2.0):
        """
        Initialize the LLM client.
        
        Args:
            endpoint_url: URL of the LLM endpoint
            api_key: API key for authentication
            min_request_interval: Minimum interval between requests in seconds (default: 2.0)
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.min_request_interval = min_request_interval
        self.last_request_time = 0.0
        self.logger = logging.getLogger(__name__)
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, 
              max_tokens: int = 1000) -> LLMResponse:
        """
        Query the LLM endpoint with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            LLMResponse: Metrics extracted from the response
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare request payload
        payload = self._prepare_payload(prompt, system_prompt, max_tokens)
        
        # Send request and measure time
        start_time = time.time()
        try:
            response = self._send_request(payload)
            response_time = time.time() - start_time
            
            # Extract metrics from response
            metrics = self._extract_metrics(response, response_time)
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error querying LLM endpoint: {e}")
            # Return a minimal response in case of error
            return LLMResponse(
                response_text=f"Error: {str(e)}",
                response_time=time.time() - start_time,
                token_count=0,
                timestamp=time.time()
            )
    
    def _apply_rate_limit(self):
        """Apply rate limiting to ensure minimum interval between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _prepare_payload(self, prompt: str, system_prompt: Optional[str], 
                        max_tokens: int) -> Dict[str, Any]:
        """
        Prepare the request payload based on common LLM API formats.
        
        This method attempts to create a payload that works with OpenAI-compatible APIs.
        For other APIs, this method may need to be overridden in a subclass.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return {
            "model": "gpt-3.5-turbo",  # Default model, can be overridden
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    
    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send the request to the LLM endpoint.
        
        Args:
            payload: The request payload
            
        Returns:
            Dict: The response from the LLM endpoint
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(
            self.endpoint_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            error_msg = f"LLM endpoint returned status code {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg += f": {error_data['error']}"
            except:
                error_msg += f": {response.text}"
            
            raise Exception(error_msg)
        
        return response.json()
    
    def _extract_metrics(self, response: Dict[str, Any], response_time: float) -> LLMResponse:
        """
        Extract metrics from the LLM response.
        
        This method attempts to extract metrics from OpenAI-compatible API responses.
        For other APIs, this method may need to be overridden in a subclass.
        
        Args:
            response: The response from the LLM endpoint
            response_time: The time taken to get the response
            
        Returns:
            LLMResponse: Metrics extracted from the response
        """
        try:
            # Extract response text (handle different API formats)
            response_text = ""
            token_count = 0
            
            if "choices" in response and len(response["choices"]) > 0:
                # OpenAI-like format
                if "message" in response["choices"][0]:
                    response_text = response["choices"][0]["message"]["content"]
                elif "text" in response["choices"][0]:
                    response_text = response["choices"][0]["text"]
            
            # Extract token count if available
            if "usage" in response and "completion_tokens" in response["usage"]:
                token_count = response["usage"]["completion_tokens"]
            
            return LLMResponse(
                response_text=response_text,
                response_time=response_time,
                token_count=token_count,
                timestamp=time.time()
            )
        except Exception as e:
            self.logger.error(f"Error extracting metrics from response: {e}")
            # Return a minimal response in case of error
            return LLMResponse(
                response_text="Error extracting response",
                response_time=response_time,
                token_count=0,
                timestamp=time.time()
            )


class AnthropicClient(LLMClient):
    """Client for interacting with Anthropic Claude API."""
    
    def _prepare_payload(self, prompt: str, system_prompt: Optional[str], 
                        max_tokens: int) -> Dict[str, Any]:
        """Prepare payload for Anthropic Claude API."""
        payload = {
            "model": "claude-2",
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.7,
            "prompt": f"Human: {prompt}\n\nAssistant:"
        }
        
        if system_prompt:
            payload["prompt"] = f"Human: {system_prompt}\n\n{prompt}\n\nAssistant:"
        
        return payload
    
    def _extract_metrics(self, response: Dict[str, Any], response_time: float) -> LLMResponse:
        """Extract metrics from Anthropic Claude API response."""
        try:
            response_text = response.get("completion", "")
            
            # Anthropic doesn't provide token count in the response
            # We'll use a rough estimate based on whitespace-split words
            token_count = len(response_text.split())
            
            return LLMResponse(
                response_text=response_text,
                response_time=response_time,
                token_count=token_count,
                timestamp=time.time()
            )
        except Exception as e:
            self.logger.error(f"Error extracting metrics from Anthropic response: {e}")
            return LLMResponse(
                response_text="Error extracting response",
                response_time=response_time,
                token_count=0,
                timestamp=time.time()
            )


def create_llm_client(endpoint_url: str, api_key: str, 
                     client_type: str = "auto") -> LLMClient:
    """
    Factory function to create an appropriate LLM client based on the endpoint URL.
    
    Args:
        endpoint_url: URL of the LLM endpoint
        api_key: API key for authentication
        client_type: Type of client to create ("auto", "openai", "anthropic")
        
    Returns:
        LLMClient: An instance of the appropriate LLM client
    """
    if client_type == "auto":
        # Try to determine client type from URL
        if "anthropic" in endpoint_url.lower():
            return AnthropicClient(endpoint_url, api_key)
        else:
            # Default to OpenAI-compatible client
            return LLMClient(endpoint_url, api_key)
    elif client_type == "anthropic":
        return AnthropicClient(endpoint_url, api_key)
    else:
        # Default to OpenAI-compatible client
        return LLMClient(endpoint_url, api_key)


# Example usage
if __name__ == "__main__":
    # This is just for demonstration purposes
    # In a real application, these would be provided as command-line arguments
    endpoint_url = "https://api.openai.com/v1/chat/completions"
    api_key = "YOUR_API_KEY"
    
    client = create_llm_client(endpoint_url, api_key)
    
    response = client.query("What is the capital of France?")
    
    print(f"Response: {response.response_text}")
    print(f"Response time: {response.response_time:.2f} seconds")
    print(f"Token count: {response.token_count}")
    print(f"Timestamp: {datetime.fromtimestamp(response.timestamp)}")