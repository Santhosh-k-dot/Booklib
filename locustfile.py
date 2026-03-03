from locust import HttpUser, task, between
import random

class LibraryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Runs when user starts.
        Login and store access token.
        """
        username = "user123123"
        password = "admin"

        # Try login
        with self.client.post(
            "/api/login",
            data={"username": username, "password": password},
            catch_response=True
        ) as response:

            if response.status_code == 200:
                token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {token}"}
            else:
                response.failure("Login failed")

    # ===================== PUBLIC =====================

    @task(5)
    def get_books(self):
        self.client.get("/api/books")

    @task(2)
    def get_single_book(self):
        book_id = random.randint(300, 500)
        self.client.get(f"/api/books/{book_id}")

    # ===================== PROTECTED =====================

    @task(3)
    def borrow_book(self):
        book_id = random.randint(40, 50)
        self.client.post(
            "/api/borrow",
            json={"book_id": book_id},
            headers=self.headers
        )

    @task(2)
    def my_transactions(self):
        self.client.get(
            "/api/transactions/my",
            headers=self.headers
        )


# ===================== ADMIN USER =====================

class AdminUser(HttpUser):
    wait_time = between(400, 500)

    def on_start(self):
        with self.client.post(
            "/api/login",
            data={"username": "user123123", "password": "admin"},
            catch_response=True
        ) as response:

            if response.status_code == 200:
                token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {token}"}
            else:
                response.failure("Admin login failed")

    @task
    def get_all_transactions(self):
        self.client.get("/api/transactions", headers=self.headers)