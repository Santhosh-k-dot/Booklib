"""
SPIKE TEST - Sudden Traffic Burst Simulation

This test simulates a sudden, massive increase in traffic to test:
- Rate limiter effectiveness
- System recovery time
- Error handling under extreme load
- Database connection pool behavior

Run with:
    locust -f locustfile_spike.py --users 1000 --spawn-rate 100 --run-time 3m --headless

Or use web UI:
    locust -f locustfile_spike.py
    Then go to http://localhost:8089 and enter:
    - Users: 1000
    - Spawn rate: 100 (100 users per second = burst to 1000 in 10 seconds)
"""

from locust import HttpUser, task, between, events
import random
from datetime import datetime


class SpikeUser(HttpUser):
    """
    Aggressive user behavior for spike testing
    Very short wait times to maximize request rate
    """
    host = "http://localhost:8000"
    wait_time = between(0.1, 0.5)  # 100-500ms between requests
    
    # Track token for authenticated requests
    token = None
    headers = {}
    
    def on_start(self):
        """Login once at the start"""
        try:
            response = self.client.post(
                "/api/login",
                data={
                    "username": f"user{random.randint(1, 100)}",
                    "password": "password123"
                },
                catch_response=True
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                # Continue without auth if login fails
                response.failure(f"Login failed: {response.status_code}")
        except Exception as e:
            print(f"Login error: {e}")
    
    @task(10)
    def get_books(self):
        """Most frequent operation - should be cached"""
        with self.client.get(
            "/api/books",
            catch_response=True,
            name="GET /api/books"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:  # Rate limited
                response.success()  # Expected during spike
            else:
                response.failure(f"Unexpected: {response.status_code}")
    
    @task(5)
    def get_book_by_id(self):
        """Random book lookups"""
        book_id = random.randint(1, 500)
        with self.client.get(
            f"/api/books/{book_id}",
            catch_response=True,
            name="GET /api/books/{id}"
        ) as response:
            if response.status_code in [200, 404, 429]:
                response.success()
            else:
                response.failure(f"Unexpected: {response.status_code}")
    
    @task(3)
    def attempt_borrow(self):
        """Try to borrow books - will hit rate limits"""
        if self.token:
            book_id = random.randint(1, 300)
            with self.client.post(
                "/api/borrow",
                headers=self.headers,
                json={"book_id": book_id},
                catch_response=True,
                name="POST /api/borrow"
            ) as response:
                if response.status_code in [201, 400, 401, 429]:
                    response.success()  # All expected
                else:
                    response.failure(f"Unexpected: {response.status_code}")
    
    @task(2)
    def my_transactions(self):
        """View transaction history"""
        if self.token:
            with self.client.get(
                "/api/transactions/my",
                headers=self.headers,
                catch_response=True,
                name="GET /api/transactions/my"
            ) as response:
                if response.status_code in [200, 401, 429]:
                    response.success()
                else:
                    response.failure(f"Unexpected: {response.status_code}")


class ExtremelyAggressiveUser(HttpUser):
    """
    Even more aggressive - minimal wait time
    Use sparingly - this will HAMMER your API
    """
    host = "http://localhost:8000"
    wait_time = between(0.05, 0.2)  # 50-200ms between requests
    weight = 1  # Only 1 in 10 users is this aggressive
    
    @task
    def rapid_fire_requests(self):
        """Rapid fire requests to test rate limiting"""
        endpoints = [
            "/api/books",
            "/health",
            "/",
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, catch_response=True)


# ============================================
# EVENT LISTENERS
# ============================================

# Track metrics for spike analysis
spike_metrics = {
    "requests_by_second": {},
    "failures_by_second": {},
    "slow_requests": 0,
    "rate_limited": 0
}


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize spike test"""
    print("\n" + "="*70)
    print("🚀 SPIKE TEST INITIALIZED")
    print("="*70)
    print("\nThis test will simulate a sudden traffic burst.")
    print("Watch for:")
    print("  - Rate limiting (429 errors)")
    print("  - Response time degradation")
    print("  - Database connection errors")
    print("  - System recovery after spike")
    print("\n" + "="*70 + "\n")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test started"""
    print(f"\n⏱️  SPIKE TEST STARTED at {datetime.now().strftime('%H:%M:%S')}\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Track request metrics"""
    current_second = datetime.now().second
    
    # Track requests per second
    if current_second not in spike_metrics["requests_by_second"]:
        spike_metrics["requests_by_second"][current_second] = 0
    spike_metrics["requests_by_second"][current_second] += 1
    
    # Track failures
    if exception:
        if current_second not in spike_metrics["failures_by_second"]:
            spike_metrics["failures_by_second"][current_second] = 0
        spike_metrics["failures_by_second"][current_second] += 1
    
    # Track slow requests
    if response_time > 1000:
        spike_metrics["slow_requests"] += 1
        print(f"⚠️  SLOW: {name} took {response_time:.0f}ms")
    
    # Track rate limiting
    if hasattr(context, 'response') and context.response.status_code == 429:
        spike_metrics["rate_limited"] += 1


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test completed - print spike analysis"""
    print("\n" + "="*70)
    print("📊 SPIKE TEST COMPLETED")
    print("="*70)
    
    stats = environment.stats
    
    print(f"\n📈 OVERALL METRICS:")
    print(f"  Total Requests:        {stats.total.num_requests:,}")
    print(f"  Total Failures:        {stats.total.num_failures:,}")
    print(f"  Requests/sec (avg):    {stats.total.total_rps:.2f}")
    print(f"  Response Time (avg):   {stats.total.avg_response_time:.2f}ms")
    print(f"  Response Time (50th):  {stats.total.get_response_time_percentile(0.5):.2f}ms")
    print(f"  Response Time (95th):  {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  Response Time (99th):  {stats.total.get_response_time_percentile(0.99):.2f}ms")
    
    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"  Failure Rate:          {failure_rate:.2f}%")
    
    print(f"\n🚦 SPIKE SPECIFIC METRICS:")
    print(f"  Slow Requests (>1s):   {spike_metrics['slow_requests']:,}")
    print(f"  Rate Limited (429):    {spike_metrics['rate_limited']:,}")
    
    # Peak requests per second
    if spike_metrics["requests_by_second"]:
        peak_rps = max(spike_metrics["requests_by_second"].values())
        print(f"  Peak Requests/sec:     {peak_rps}")
    
    print("\n🎯 RECOMMENDATIONS:")
    
    # Analyze results and provide recommendations
    if stats.total.avg_response_time > 500:
        print("  ⚠️  High average response time - consider:")
        print("      - Increase cache TTL")
        print("      - Add more worker processes")
        print("      - Optimize database queries")
    
    if failure_rate > 5:
        print("  ❌ High failure rate - investigate:")
        print("      - Database connection pool size")
        print("      - Application errors in logs")
        print("      - Resource exhaustion (CPU/memory)")
    
    if spike_metrics['rate_limited'] > stats.total.num_requests * 0.3:
        print("  ⚠️  Many requests rate limited (>30%) - consider:")
        print("      - Adjusting rate limit thresholds")
        print("      - Implementing queue system")
        print("      - Adding load balancer")
    else:
        print("  ✅ Rate limiting working as expected")
    
    if stats.total.avg_response_time < 200 and failure_rate < 1:
        print("  ✅ System handled spike well!")
    
    print("\n" + "="*70 + "\n")


# ============================================
# USAGE INSTRUCTIONS
# ============================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                    SPIKE TEST INSTRUCTIONS                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  Quick Start:                                                   ║
║    locust -f locustfile_spike.py                               ║
║    Open http://localhost:8089                                  ║
║                                                                 ║
║  Recommended Spike Test Settings:                              ║
║    Users: 1000                                                 ║
║    Spawn rate: 100 (burst in 10 seconds)                      ║
║    Duration: 3 minutes                                         ║
║                                                                 ║
║  Headless Mode:                                                ║
║    locust -f locustfile_spike.py \\                            ║
║      --users 1000 \\                                           ║
║      --spawn-rate 100 \\                                       ║
║      --run-time 3m \\                                          ║
║      --headless \\                                             ║
║      --html spike_report.html                                  ║
║                                                                 ║
║  Extreme Spike (use with caution):                            ║
║    --users 2000 --spawn-rate 200                              ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
    """)