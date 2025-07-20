from .bedrock_worker import BedrockAPIWorker
from .claude_worker import ClaudeAPIWorker
from .cohere_worker import CohereAPIWorker
from .gemini_worker import GeminiAPIWorker
from .groq_worker import GroqAPIWorker
from .mistral_worker import MistralAPIWorker
from .openai_worker import OpenAIAPIWorker
from .ollama_worker import OllamaAPIWorker

def get_worker(worker_type, **kwargs):
    """
    Factory function to get a worker instance.
    """
    worker_classes = {
        "bedrock": BedrockAPIWorker,
        "claude": ClaudeAPIWorker,
        "cohere": CohereAPIWorker,
        "gemini": GeminiAPIWorker,
        "groq": GroqAPIWorker,
        "mistral": MistralAPIWorker,
        "openai": OpenAIAPIWorker,
        "ollama": OllamaAPIWorker,
    }
    worker_class = worker_classes.get(worker_type)
    if worker_class:
        return worker_class(**kwargs)
    else:
        raise ValueError(f"Unsupported worker type: {worker_type}")
