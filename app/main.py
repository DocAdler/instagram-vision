import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from instagrapi import Client

app = FastAPI()
_sessions: dict[str, Client] = {}


@app.get("/")
def root():
    """Simple landing message."""
    return {
        "message": "Instagram Vision API",
        "docs": "/docs",
    }


class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None
    sessionid: str | None = None


@app.post("/login")
def login(req: LoginRequest):
    """Create an authenticated or anonymous session.

    If no credentials are supplied an anonymous session is returned. Some
    endpoints may fail when used anonymously, but basic data can still be
    retrieved.
    """

    client = Client()
    if req.sessionid:
        client.sessionid = req.sessionid
        try:
            client.user_info(client.user_id_from_username("instagram"))
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
    elif req.username and req.password:
        try:
            client.login(req.username, req.password)
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    token = str(uuid.uuid4())
    _sessions[token] = client
    return {"token": token}


@app.post("/logout")
def logout(token: str = Query(...)):
    """Remove an authenticated session."""
    if token in _sessions:
        _sessions.pop(token)
        return {"detail": "Logged out"}
    raise HTTPException(status_code=401, detail="Invalid token")


def get_client(token: str) -> Client:
    client = _sessions.get(token)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid token")
    return client


@app.get("/profile/{username}")
def profile(username: str, token: str = Query(...)):
    client = get_client(token)
    info = client.user_info_by_username(username)
    return {
        "username": info.username,
        "full_name": info.full_name,
        "biography": info.biography,
        "followers": info.follower_count,
        "followees": info.following_count,
        "is_private": info.is_private,
        "profile_pic_url": info.profile_pic_url,
    }


@app.get("/posts/{username}")
def posts(username: str, token: str = Query(...), limit: int = 5):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    medias = client.user_medias(user_id, amount=limit)
    items = [
        {
            "id": m.id,
            "shortcode": m.code,
            "caption": m.caption_text,
            "url": m.thumbnail_url,
            "taken_at": m.taken_at.isoformat(),
        }
        for m in medias
    ]
    return {"posts": items}


@app.get("/comments/{media_id}")
def comments(media_id: str, token: str = Query(...), limit: int = 20):
    client = get_client(token)
    cmts = client.media_comments(media_id, amount=limit)
    items = [
        {
            "id": c.pk,
            "user": c.user.username,
            "text": c.text,
            "created_at": c.created_at.isoformat(),
        }
        for c in cmts
    ]
    return {"comments": items}


@app.get("/stories/{username}")
def stories(username: str, token: str = Query(...)):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    sts = client.user_stories(user_id)
    items = [{"id": s.pk, "url": s.thumbnail_url, "taken_at": s.taken_at.isoformat()} for s in sts]
    return {"stories": items}


@app.get("/followers/{username}")
def followers(username: str, token: str = Query(...), limit: int = 20):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    data = client.user_followers(user_id, amount=limit)
    return {"followers": [u.username for u in data.values()]}


@app.get("/followings/{username}")
def followings(username: str, token: str = Query(...), limit: int = 20):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    data = client.user_following(user_id, amount=limit)
    return {"followings": [u.username for u in data.values()]}


@app.get("/hashtag/{tag}")
def hashtag(tag: str, token: str = Query(...), limit: int = 10):
    client = get_client(token)
    medias = client.hashtag_medias_recent(tag, amount=limit)
    items = [
        {
            "id": m.id,
            "shortcode": m.code,
            "caption": m.caption_text,
            "url": m.thumbnail_url,
        }
        for m in medias
    ]
    return {"hashtag": tag, "posts": items}


@app.get("/reels/{username}")
def reels(username: str, token: str = Query(...), limit: int = 5):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    clips = client.user_clips(user_id, amount=limit)
    items = [
        {
            "id": c.id,
            "shortcode": c.code,
            "caption": c.caption_text,
            "url": c.thumbnail_url,
        }
        for c in clips
    ]
    return {"reels": items}


@app.get("/highlights/{username}")
def highlights(username: str, token: str = Query(...)):
    client = get_client(token)
    user_id = client.user_id_from_username(username)
    hl_list = client.highlights_user(user_id)
    items = []
    for hl in hl_list:
        for m in client.highlight_medias(hl.id):
            items.append(
                {
                    "id": m.id,
                    "title": hl.title,
                    "url": m.thumbnail_url,
                    "taken_at": m.taken_at.isoformat(),
                }
            )
    return {"highlights": items}


@app.get("/download/{media_id}")
def download(media_id: str, token: str = Query(...)):
    client = get_client(token)
    info = client.media_info(media_id)
    if info.media_type == 1:
        path = client.photo_download(info.pk)
    elif info.media_type == 2:
        path = client.video_download(info.pk)
    elif info.media_type == 8:
        path = client.album_download(info.pk)
    else:
        raise HTTPException(status_code=400, detail="Unsupported media type")
    return FileResponse(path, filename=Path(path).name)
