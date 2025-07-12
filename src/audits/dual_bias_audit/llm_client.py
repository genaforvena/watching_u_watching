import time
import requests

class LLMClient:
    def __init__(self, endpoint, api_key, rate_limit_s=2):
        self.endpoint = endpoint
        self.api_key = api_key
        self.rate_limit_s = rate_limit_s

    def query(self, probe):
        # POST to LLM endpoint, respecting rate limit
        payload = {"prompt": probe["prompt"], "api_key": self.api_key}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.endpoint, json=payload, headers=headers)
        time.sleep(self.rate_limit_s)
        return response.json()