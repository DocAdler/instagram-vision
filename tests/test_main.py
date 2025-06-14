from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
import app.main as main_module

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


def test_download_cleans_up(tmp_path):
    token = "test-token"
    file_path = tmp_path / "dummy.txt"
    file_path.write_text("hello")

    class DummyInfo:
        media_type = 1
        pk = "abc"

    class DummyClient:
        def media_info(self, media_id):
            return DummyInfo()

        def photo_download(self, pk):
            return str(file_path)

    main_module._sessions[token] = DummyClient()

    resp = client.get(f"/download/123", params={"token": token})
    assert resp.status_code == 200
    assert not file_path.exists()
    main_module._sessions.pop(token, None)
