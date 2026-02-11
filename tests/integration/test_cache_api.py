def test_books_cache(client):
    response1 = client.get("/api/books")
    response2 = client.get("/api/books")

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Optional: response consistency
    assert response1.json() == response2.json()