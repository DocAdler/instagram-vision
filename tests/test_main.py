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


def test_profile_posts_comments():
    resp = client.post("/login", json={})
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert token

    class DummyUserInfo:
        username = "john"
        full_name = "John Doe"
        biography = "bio"
        follower_count = 5
        following_count = 2
        is_private = False
        profile_pic_url = "http://example.com/john.jpg"

    class DummyUser:
        def __init__(self, username):
            self.username = username

    class DummyComment:
        def __init__(self, pk, text):
            self.pk = pk
            self.user = DummyUser("john")
            self.text = text

            from datetime import datetime

            self.created_at = datetime(2021, 1, 1)

    class DummyMedia:
        def __init__(self, ident):
            self.id = ident
            self.code = f"code{ident}"
            self.caption_text = f"caption{ident}"
            self.thumbnail_url = f"http://example.com/{ident}.jpg"

            from datetime import datetime

            self.taken_at = datetime(2021, 1, ident)

    class DummyClient:
        def user_info_by_username(self, username):
            return DummyUserInfo()

        def user_id_from_username(self, username):
            return "123"

        def user_medias(self, user_id, amount=5):
            return [DummyMedia(i) for i in range(1, amount + 1)]

        def media_comments(self, media_id, amount=20):
            return [DummyComment(i, f"text{i}") for i in range(1, amount + 1)]

    main_module._sessions[token] = DummyClient()

    resp = client.get("/profile/john", params={"token": token})
    assert resp.status_code == 200
    assert resp.json()["username"] == "john"
    assert resp.json()["followers"] == 5

    resp = client.get("/posts/john", params={"token": token, "limit": 2})
    assert resp.status_code == 200
    posts = resp.json().get("posts", [])
    assert len(posts) == 2
    assert posts[0]["id"] == 1

    resp = client.get("/comments/1", params={"token": token, "limit": 3})
    assert resp.status_code == 200
    comments = resp.json().get("comments", [])
    assert len(comments) == 3
    assert comments[0]["text"] == "text1"

    main_module._sessions.pop(token, None)
