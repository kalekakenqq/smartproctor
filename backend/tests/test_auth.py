from backend.tests.conftest import register_user


def test_register_creates_user(client):
    resp = register_user(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "user@test.com"
    assert body["user"]["role"] == "student"
    assert "access_token" in body


def test_register_duplicate_email_fails(client):
    register_user(client)
    resp = register_user(client)
    assert resp.status_code == 400


def test_login_success(client):
    register_user(client)
    resp = client.post("/auth/login", json={"email": "user@test.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_fails(client):
    register_user(client)
    resp = client.post("/auth/login", json={"email": "user@test.com", "password": "wrong-password"})
    assert resp.status_code == 401


def test_protected_endpoint_requires_token(client):
    resp = client.get("/tests")
    assert resp.status_code == 401
