
from locust import HttpUser, between, task

import uuid


class LibraryUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)

    @task(3)
    def get_books(self):
        self.client.get("/api/books")

    @task(2)
    def create_book(self):
        uid = str(uuid.uuid4())[:8]
        self.client.post("/api/books", json={
            "title": f"Load Book {uid}",
            "author": "Tester",
            "isbn": f"ISBN-{uid}",
            "total_copies": 5
        })

    @task(1)
    def register_user(self):
        uid = str(uuid.uuid4())[:8]
        self.client.post("/api/register", json={
            "email": f"load{uid}@test.com",
            "username": f"loaduser_{uid}",
            "password": "password123",
            "full_name": "Load User"
        })