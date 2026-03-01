"""
Comprehensive Load Testing Suite for Library Management System

Test Types:
1. Load Test: Simulates normal expected traffic
2. Stress Test: Pushes system beyond normal capacity
3. Spike Test: Sudden burst of traffic
4. Endurance Test: Sustained load over time

Run with:
- Load Test: locust -f locustfile_comprehensive.py --users 50 --spawn-rate 5 --run-time 5m
- Stress Test: locust -f locustfile_comprehensive.py --users 200 --spawn-rate 10 --run-time 10m
- Spike Test: locust -f locustfile_comprehensive.py --users 500 --spawn-rate 50 --run-time 2m
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime


class LibraryUser(HttpUser):
    """Simulates a regular library user"""
    host = "http://localhost:8000"
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    # Credentials pool for testing
    user_credentials = [
        {"username": "user123123", "password": "admin"},
        # {"username": "sunitha", "password": "admin"},
        # {"username": "getha", "password": "admin"},
        # {"username": "ramesh123", "password": "admin"},
    ]
    
    def on_start(self):
        """Called when a simulated user starts - handles login"""
        # Randomly select credentials
        creds = random.choice(self.user_credentials)
        
        # Login and get token
        with self.client.post(
            "/api/login",
            data={
                "username": creds["username"],
                "password": creds["password"]
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.refresh_token = response.json()["refresh_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")
                self.token = None
                self.headers = {}
    
    @task(10)
    def browse_books(self):
        """Most common action - browse available books"""
        self.client.get("/api/books", name="GET /api/books")
    
    @task(5)
    def view_book_details(self):
        """View details of a specific book"""
        # Random book ID between 1-300
        book_id = random.randint(210, 244)
        self.client.get(f"/api/books/{book_id}", name="GET /api/books/{id}")
    
    @task(3)
    def view_my_transactions(self):
        """Check user's borrowing history"""
        if self.token:
            self.client.get(
                "/api/transactions/my",
                headers=self.headers,
                name="GET /api/transactions/my"
            )
    
    @task(2)
    def borrow_book(self):
        """Attempt to borrow a book"""
        if self.token:
            book_id = random.randint(210, 244)
            with self.client.post(
                "/api/borrow",
                headers=self.headers,
                json={"book_id": book_id},
                catch_response=True,
                name="POST /api/borrow"
            ) as response:
                if response.status_code == 201:
                    response.success()
                    # Store transaction ID for potential return
                    try:
                        self.last_transaction_id = response.json()["id"]
                    except:
                        pass
                elif response.status_code == 400:
                    # Expected errors (book unavailable, already borrowed)
                    response.success()
                else:
                    response.failure(f"Unexpected: {response.status_code}")
    
    @task(1)
    def return_book(self):
        """Return a previously borrowed book"""
        if self.token and hasattr(self, 'last_transaction_id'):
            self.client.post(
                f"/api/return/{self.last_transaction_id}",
                headers=self.headers,
                name="POST /api/return/{id}"
            )
    
    @task(1)
    def refresh_token_endpoint(self):
        """Refresh access token"""
        if hasattr(self, 'refresh_token'):
            with self.client.post(
                "/api/refresh",
                json={"refresh_token": self.refresh_token},
                catch_response=True,
                name="POST /api/refresh"
            ) as response:
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    self.refresh_token = response.json()["refresh_token"]
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    response.success()


class AdminUser(HttpUser):
    """Simulates an admin user with heavier operations"""
    host = "http://localhost:8000"
    wait_time = between(2, 5)
    weight = 1  # Only 1 admin for every 10 regular users
    
    def on_start(self):
        """Admin login"""
        # Use admin credentials
        response = self.client.post(
            "/api/login",
            data={
                "username": "user123123",
                "password": "admin"
            }
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(5)
    def view_all_transactions(self):
        """Admin views all transactions"""
        if self.token:
            self.client.get(
                "/api/transactions",
                headers=self.headers,
                name="GET /api/transactions (admin)"
            )
    
    @task(3)
    def view_all_users(self):
        """Admin views all users"""
        if self.token:
            self.client.get(
                "/api/users",
                headers=self.headers,
                name="GET /api/users (admin)"
            )
    
    @task(2)
    def create_book(self):
        """Admin creates a new book"""
        if self.token:
            book_data = {
                "title": f"Test Book {random.randint(1000, 9999)}",
                "author": f"Author {random.randint(1, 100)}",
                "isbn": f"ISBN-{random.randint(1000000, 9999999)}",
                "total_copies": random.randint(1, 10),
                "description": "Load test book"
            }
            with self.client.post(
                "/api/books",
                headers=self.headers,
                json=book_data,
                catch_response=True,
                name="POST /api/books (admin)"
            ) as response:
                if response.status_code in [201, 400]:  # 400 = duplicate ISBN
                    response.success()
    
    @task(1)
    def update_book(self):
        """Admin updates a book"""
        if self.token:
            book_id = random.randint(210, 244)
            update_data = {
                "description": f"Updated at {datetime.now().isoformat()}"
            }
            self.client.put(
                f"/api/books/{book_id}",
                headers=self.headers,
                json=update_data,
                name="PUT /api/books/{id} (admin)"
            )


class ReadOnlyUser(HttpUser):
    """Simulates users who only browse (no authentication needed)"""
    host = "http://localhost:8000"
    wait_time = between(0.5, 2)  # Faster browsing
    weight = 3  # More read-only users
    
    @task(10)
    def browse_books(self):
        """Browse books without authentication"""
        self.client.get("/api/books", name="GET /api/books (public)")
    
    @task(5)
    def view_book_details(self):
        """View book details"""
        book_id = random.randint(210, 244)
        self.client.get(f"/api/books/{book_id}", name="GET /api/books/{id} (public)")
    
    @task(1)
    def health_check(self):
        """Check API health"""
        self.client.get("/health", name="GET /health")


# ============================================
# SPIKE TEST USER (for sudden traffic bursts)
# ============================================

class SpikeTestUser(HttpUser):
    """
    Aggressive user for spike testing
    Run with: locust -f locustfile_comprehensive.py --users 500 --spawn-rate 100 --run-time 2m
    """
    host = "http://localhost:8000"
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task
    def rapid_browse(self):
        """Rapid browsing simulation"""
        self.client.get("/api/books")


# ============================================
# EVENT LISTENERS (for detailed reporting)
# ============================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*60)
    print("LOAD TEST STARTED")
    print(f"Test Type: {environment.parsed_options.tags or 'Standard Load Test'}")
    print(f"Start Time: {datetime.now()}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "="*60)
    print("LOAD TEST COMPLETED")
    print(f"End Time: {datetime.now()}")
    
    stats = environment.stats
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    
    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")
    
    print("="*60 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 2000:  # Log requests slower than 2 seconds
        print(f"⚠️  SLOW REQUEST: {name} took {response_time:.0f}ms")
    
    if exception:
        print(f"❌ ERROR: {name} - {exception}")