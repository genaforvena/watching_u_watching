import importlib

def get_worker(worker_type, **kwargs):
    """
    Factory function to get a worker instance.
    """
    try:
        module = importlib.import_module(f".{worker_type}_worker", package="implementations.cryptohauntological_probe.llm_apis")
        if worker_type in ['openai', 'qwen', 'deepseek', 'kimi']:
            worker_class_name = f"{worker_type.capitalize()}APIWorker"
            if worker_type == 'openai':
                worker_class_name = "OpenAIAPIWorker"
        else:
            worker_class_name = f"{worker_type.capitalize()}APIWorker"
        worker_class = getattr(module, worker_class_name)
        return worker_class(**kwargs)
    except (ImportError, AttributeError):
        raise ValueError(f"Unsupported worker type: {worker_type}")
