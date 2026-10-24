"""Example usage for GenPark Sliding Log Rate Limiter."""
from client import SlidingLogRateLimiter

def main():
    limiter = SlidingLogRateLimiter()
    client = "agent_worker_01"

    print("Checking sliding window rate limits (capacity: 5 req / 10s)...")
    for i in range(6):
        res = limiter.allow_request(client, max_requests=5, window_seconds=10.0)
        print(f"Request #{i+1}: Allowed={res['allowed']}, Remaining={res['remaining_quota']}")

    status = limiter.get_rate_status(client, max_requests=5, window_seconds=10.0)
    print("
Client Status:", status)

if __name__ == "__main__":
    main()
