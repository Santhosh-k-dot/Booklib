import uuid

def test_register_user(client):
    uid = uuid.uuid4().hex[:8]

    response = client.post("/api/register", json={
        "email": f"{uid}@example.com",
        "username": f"user_{uid}",
        "password": "password123",
        "full_name": "Test User"
    })

    assert response.status_code == 200

def test_login_user(client):
    response = client.post("/api/login", json={
        "username": "testuser1",
        "password": "password123"
    })


def test_get_all_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200