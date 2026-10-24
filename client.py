"""Sliding Log Rate Limiter.
100% Python Standard Library.
"""
import time
from typing import Dict, Any, List

class SlidingLogRateLimiter:
    """Sliding window log rate limiter with microsecond precision."""
    def __init__(self):
        self.logs: Dict[str, List[float]] = {}

    def allow_request(self, client_id: str, max_requests: int = 60, window_seconds: float = 60.0) -> Dict[str, Any]:
        now = time.time()
        cutoff = now - window_seconds

        if client_id not in self.logs:
            self.logs[client_id] = []

        self.logs[client_id] = [ts for ts in self.logs[client_id] if ts > cutoff]

        allowed = len(self.logs[client_id]) < max_requests
        if allowed:
            self.logs[client_id].append(now)

        remaining = max(0, max_requests - len(self.logs[client_id]))
        reset_time = (self.logs[client_id][0] + window_seconds - now) if self.logs[client_id] else 0.0

        return {
            "allowed": allowed,
            "client_id": client_id,
            "current_requests": len(self.logs[client_id]),
            "max_requests": max_requests,
            "remaining_quota": remaining,
            "window_seconds": window_seconds,
            "reset_seconds": max(0.0, round(reset_time, 2))
        }

    def get_rate_status(self, client_id: str, max_requests: int = 60, window_seconds: float = 60.0) -> Dict[str, Any]:
        now = time.time()
        cutoff = now - window_seconds
        valid_logs = [ts for ts in self.logs.get(client_id, []) if ts > cutoff]
        self.logs[client_id] = valid_logs

        req_count = len(valid_logs)
        remaining = max(0, max_requests - req_count)
        utilization = (req_count / max_requests * 100.0) if max_requests > 0 else 0.0
        return {
            "client_id": client_id,
            "current_requests": req_count,
            "max_requests": max_requests,
            "remaining_quota": remaining,
            "utilization_percent": round(utilization, 2)
        }

    def reset_rate_log(self, client_id: str) -> Dict[str, Any]:
        if client_id in self.logs:
            del self.logs[client_id]
        return {"status": "reset", "client_id": client_id}
