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
            "qwen": "Qwen",
            "bedrock": "Bedrock",
            "claude": "Claude",
            "cohere": "Cohere",
            "gemini": "Gemini",
            "groq": "Groq",
            "mistral": "Mistral",
            "ollama": "Ollama"
        }
        worker_class_name = f"{worker_name_map.get(worker_type.lower(), worker_type.capitalize())}APIWorker"
        worker_class = getattr(module, worker_class_name)
        
        # Handle special cases for workers with specific requirements
        if worker_type.lower() == "bedrock" and "region" not in kwargs:
            kwargs["region"] = "us-east-1"  # Default region
        
        return worker_class(**kwargs)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unsupported worker type: {worker_type}. Error: {str(e)}")
    except ValueError as e:
        # Re-raise ValueError from worker initialization (e.g., missing API keys)
        raise e
    except Exception as e:
        # More specific error handling for missing dependencies
        if "dashscope" in str(e).lower():
            raise ValueError(f"Qwen worker requires 'dashscope' package. Install with: pip install dashscope")
        elif "boto3" in str(e).lower():
            raise ValueError(f"Bedrock worker requires 'boto3' package and AWS credentials")
        raise ValueError(f"Error initializing {worker_type} worker: {str(e)}")
