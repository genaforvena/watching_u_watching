import importlib

def get_worker(worker_type, **kwargs):
    """
    Factory function to get a worker instance.
    """
    try:
        module = importlib.import_module(f".{worker_type}_worker", package="implementations.cryptohauntological_probe.llm_apis")
        worker_name_map = {
            "openai": "OpenAI",
            "deepseek": "DeepSeek",
            "kimi": "Kimi",
            "qwen": "Qwen"
        }
        worker_class_name = f"{worker_name_map.get(worker_type.lower(), worker_type.capitalize())}APIWorker"
        worker_class = getattr(module, worker_class_name)
        return worker_class(**kwargs)
    except (ImportError, AttributeError):
        raise ValueError(f"Unsupported worker type: {worker_type}")
