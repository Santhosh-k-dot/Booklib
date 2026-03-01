from urllib import response
import uuid

def test_create_book(client):
    response = client.post("/api/books", json={
        "title": "Clean Code",
        "author": "Robert Martin",
        "isbn": f"ISBN-{uuid.uuid4()}",
        "total_copies": 5
    })

    assert response.status_code == 201
    assert response.json()["available_copies"] == 5

def test_get_books(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_book(client):
    create = client.post("/api/books", json={
        "title": "Temp Book",
        "author": "Temp Author",
        "isbn": f"TEMP-{uuid.uuid4()}",
        "total_copies": 5
    })

    book_id = create.json()["id"]

    update = client.put(f"/api/books/{book_id}", json={
        "total_copies": 10
    })

    assert update.status_code == 200
    assert update.json()["total_copies"] == 10
def test_delete_book(client):
    create = client.post("/api/books", json={
        "title": "Delete Book",
        "author": "Author",
        "isbn": f"DEL-{uuid.uuid4()}",
        "total_copies": 1
    })

    assert create.status_code == 201   # 🔥test_borrow_book

    book_id = create.json()["id"]

    