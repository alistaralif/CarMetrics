import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()
    
    def is_allowed(self, key: str, max_urls: int, window_seconds: int, url_count: int) -> tuple[bool, int]:
        """
        Check if request is allowed based on URL count within time window.
        Returns (is_allowed, seconds_until_reset).
        """
        now = time.time()
        
        with self._lock:
            # Clean old entries
            self._requests[key] = [
                (ts, count) for ts, count in self._requests[key]
                if now - ts < window_seconds
            ]
            
            # Calculate total URLs in window
            total_urls = sum(count for _, count in self._requests[key])
            
            if total_urls + url_count > max_urls:
                # Find when the oldest request expires
                if self._requests[key]:
                    oldest = min(ts for ts, _ in self._requests[key])
                    wait_time = int(window_seconds - (now - oldest)) + 1
                else:
                    wait_time = window_seconds
                return False, wait_time
            
            # Record this request
            self._requests[key].append((now, url_count))
            return True, 0

# Global instance
rate_limiter = RateLimiter()