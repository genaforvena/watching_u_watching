import importlib

def get_worker(worker_type, **kwargs):
    """
    Factory function to get a worker instance.
    """
    try:
        module = importlib.import_module(f".{worker_type}_worker", package="implementations.cryptohauntological_probe.llm_apis")
        worker_class = getattr(module, f"{'OpenAI' if worker_type == 'openai' else worker_type.capitalize()}APIWorker")
        return worker_class(**kwargs)
    except (ImportError, AttributeError):
        raise ValueError(f"Unsupported worker type: {worker_type}")
