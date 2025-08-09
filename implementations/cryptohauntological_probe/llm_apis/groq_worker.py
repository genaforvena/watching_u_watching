import os
from groq import Groq
from typing import List, Tuple
import re
import time
import random
import logging

try:
    from groq import RateLimitError
except ImportError:
    class RateLimitError(Exception):
        pass

class GroqAPIWorker:
    def __init__(self, api_key: str = None, model_name: str = "llama3-8b-8192", 
                 context_window_limit: int = 2048, timeout: int = 120,
                 max_retries: int = None, backoff_seconds: float = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key must be provided via argument or GROQ_API_KEY env var.")
        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name
        self.context_window_limit = context_window_limit
        self.timeout = timeout
        self.max_retries = max_retries if max_retries is not None else int(os.getenv("GROQ_MAX_RETRIES", "5"))
        self.backoff_seconds = backoff_seconds if backoff_seconds is not None else float(os.getenv("GROQ_BACKOFF", "2.0"))

    def _build_history(self, history: List[Tuple[str, str]], user_query: str) -> list:
        messages = []
        for user_turn, ai_turn in history:
            messages.append({"role": "user", "content": user_turn})
            messages.append({"role": "assistant", "content": ai_turn})
        messages.append({"role": "user", "content": user_query})
        return messages

    def _truncate_messages(self, messages: list) -> list:
        """Soft-trim history to fit approximate token budget."""
        if not self.context_window_limit:
            return messages
        char_budget = int(self.context_window_limit * 4)
        total = 0
        kept = []
        for msg in reversed(messages):
            c = len(msg.get("content", ""))
            if total + c > char_budget and kept:
                break
            kept.append(msg)
            total += c
        return list(reversed(kept))

    def _parse_retry_after(self, error_msg: str) -> float:
        """Parse server-suggested wait time from error message."""
        # Pattern: "Please try again in 5m16.871s"
        m = re.search(r"Please try again in\s*(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?", error_msg)
        if m:
            minutes = int(m.group(1)) if m.group(1) else 0
            seconds = float(m.group(2)) if m.group(2) else 0
            total_seconds = minutes * 60 + seconds
            logging.info(f"Server requested wait: {total_seconds:.1f}s")
            return total_seconds
        return None

    def _calculate_backoff(self, attempt: int, server_wait: float = None) -> float:
        """Calculate wait time: server suggestion or exponential backoff."""
        if server_wait:
            # Add small buffer to server suggestion
            return server_wait + random.uniform(1, 5)
        
        # Exponential backoff with jitter
        base = self.backoff_seconds * (2 ** attempt)
        jitter = random.uniform(0, self.backoff_seconds)
        return min(base + jitter, 300.0)  # Cap at 5 minutes

    def reply(self, prompt: str, memory: List[Tuple[str, str]] = None) -> str:
        memory = memory or []
        messages = self._build_history(memory, prompt)
        messages = self._truncate_messages(messages)

        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model_name,
                )
                return chat_completion.choices[0].message.content
                
            except (RateLimitError, Exception) as e:
                last_exception = e
                error_msg = str(e)
                
                # Check if it's a rate limit error
                is_rate_limit = (
                    "429" in error_msg or 
                    "Rate limit" in error_msg or 
                    "Too Many Requests" in error_msg or
                    isinstance(e, RateLimitError)
                )
                
                if is_rate_limit and attempt < self.max_retries:
                    server_wait = self._parse_retry_after(error_msg)
                    wait_time = self._calculate_backoff(attempt, server_wait)
                    
                    logging.warning(f"Rate limit hit (attempt {attempt + 1}/{self.max_retries + 1}). "
                                  f"Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                elif "timeout" in error_msg.lower() and attempt < self.max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    logging.warning(f"Timeout error (attempt {attempt + 1}/{self.max_retries + 1}). "
                                  f"Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Non-retryable error or max retries exceeded
                    break
        
        # Exhausted retries
        raise last_exception or RuntimeError("Groq reply failed after retries.")
