import pytest
from fastapi.testclient import TestClient
import bcrypt
from main import app, USERS_DB

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    USERS_DB.clear()
    hashed_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
    USERS_DB["admin"] = {
        "password": hashed_pw,
        "roles": ["ROLE_ADMIN"]
    }

def test_login():
    response = client.post("/login", json={"username": "duch", "password": "123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    response = client.post("/login", json={"username": "admin", "password": "zle_haslo"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_users_creation():
    login_res = client.post("/login", json={"username": "admin", "password": "admin123"})
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    new_user = {"username": "jan_kowalski", "password": "tajne", "roles": ["ROLE_USER"]}
    response = client.post("/users", json=new_user, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User 'jan_kowalski' created successfully"

    response = client.post("/users", json=new_user, headers=admin_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

    user_login = client.post("/login", json={"username": "jan_kowalski", "password": "tajne"})
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post(
        "/users",
        json={"username": "hacker", "password": "123", "roles": ["ROLE_ADMIN"]},
        headers=user_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"

def test_user_details():
    response = client.get("/user_details")
    assert response.status_code in [401, 403]
    assert response.json()["detail"] == "Not authenticated"

    response = client.get("/user_details", headers={"Authorization": "Bearer bzdurny_token_123"})
    assert response.status_code == 401

    login_res = client.post("/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]

    response = client.get("/user_details", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin"