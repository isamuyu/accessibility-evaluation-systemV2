import pytest
from tests.conftest import client, setup_db


class TestAuth:
    """认证接口"""

    def test_register_and_login(self, setup_db):
        resp = client.post("/auth/register", json={
            "username": "tester", "password": "secret123", "full_name": "测试员"
        })
        assert resp.status_code == 200
        assert resp.json()["username"] == "tester"
        assert "hashed_password" not in resp.json()

        resp = client.post("/auth/login", json={"username": "tester", "password": "secret123"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        assert token

        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "tester"

    def test_register_duplicate_username_rejected(self, setup_db):
        client.post("/auth/register", json={"username": "tester", "password": "secret123"})
        resp = client.post("/auth/register", json={"username": "tester", "password": "other456"})
        assert resp.status_code == 400

    def test_login_wrong_password(self, setup_db):
        client.post("/auth/register", json={"username": "tester", "password": "secret123"})
        resp = client.post("/auth/login", json={"username": "tester", "password": "wrong"})
        assert resp.status_code == 401

    def test_me_without_token_rejected(self, setup_db):
        client.headers.pop("Authorization", None)
        try:
            assert client.get("/auth/me").status_code == 401
        finally:
            token = client.post("/auth/login", json={"username": "testadmin", "password": "test123456"}).json()["access_token"]
            client.headers["Authorization"] = f"Bearer {token}"

    def test_me_with_invalid_token_rejected(self, setup_db):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
        assert resp.status_code == 401

    def test_short_password_rejected(self, setup_db):
        resp = client.post("/auth/register", json={"username": "tester", "password": "123"})
        assert resp.status_code == 422
