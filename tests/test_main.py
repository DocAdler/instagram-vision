from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Instagram Vision API" in resp.json().get("message", "")


def test_login_logout():
    # anonymous login
    resp = client.post("/login", json={})
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert token

    resp = client.post("/logout", params={"token": token})
    assert resp.status_code == 200
    assert resp.json().get("detail") == "Logged out"
