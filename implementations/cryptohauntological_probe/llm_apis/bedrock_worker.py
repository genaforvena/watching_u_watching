import os
import boto3
import json
from typing import List, Tuple

class BedrockAPIWorker:
    def __init__(self, model_name: str = "anthropic.claude-3-sonnet-20240229-v1:0", context_window_limit: int = 2048, timeout: int = 120, region: str = "us-east-1"):
        if not region:
            raise ValueError("You must specify a region for Bedrock.")
        self.client = boto3.client(service_name="bedrock-runtime", region_name=region)
        self.model_name = model_name
        self.context_window_limit = context_window_limit
        self.timeout = timeout

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "user", "content": [{"type": "text", "text": user_turn}]})
            messages.append({"role": "assistant", "content": [{"type": "text", "text": ai_turn}]})
        messages.append({"role": "user", "content": [{"type": "text", "text": user_query}]})
        return messages

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": messages
        })

        response = self.client.invoke_model(
            body=body,
            modelId=self.model_name,
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0].get("text")
