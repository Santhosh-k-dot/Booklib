from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)


def unique(value: str) -> str:
    return f"{value}-{uuid.uuid4()}"


def test_borrow_book(client):
    user = client.post("/api/register", json={
        "email": f"{uuid.uuid4()}@test.com",
        "username": f"user_{uuid.uuid4()}",
        "password": "password123",
        "full_name": "Borrow User"
    }).json()

    book = client.post("/api/books", json={
        "title": "Borrow Book",
        "author": "Author",
        "isbn": f"ISBN-{uuid.uuid4()}",
        "total_copies": 2
    }).json()

    response = client.post("/api/borrow", json={
        "book_id": book["id"]
    })

    assert response.status_code == 201
    assert response.json()["status"] == "borrowed"


def test_return_book(client):
    user = client.post("/api/register", json={
        "email": f"{uuid.uuid4()}@test.com",
        "username": f"return_user_{uuid.uuid4()}",
        "password": "password123",
        "full_name": "Return User"
    }).json()

    book = client.post("/api/books", json={
        "title": "Return Book",
        "author": "Author",
        "isbn": f"RETURN-{uuid.uuid4()}",
        "total_copies": 1
    }).json()

    borrow = client.post("/api/borrow", json={
        "book_id": book["id"]
    }).json()

    response = client.post(f"/api/return/{borrow['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "returned"


def test_get_transactions(client):
    response = client.get("/api/transactions")
    assert response.status_code == 200
