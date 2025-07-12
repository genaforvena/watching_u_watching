import time
import threading
from functools import wraps

def rate_limiter(requests: int, period: int):
    """
    Simple rate limiter decorator.
    Args:
        requests: Number of allowed requests
        period: Time period in seconds
    """
    lock = threading.Lock()
    call_times = []
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.time()
                # Remove timestamps outside the period
                while call_times and call_times[0] <= now - period:
                    call_times.pop(0)
                if len(call_times) >= requests:
                    raise Exception(f"Rate limit exceeded: {requests} calls per {period} seconds")
                call_times.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
