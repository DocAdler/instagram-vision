import uuid
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import instaloader

app = FastAPI()

_sessions = {}


class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None
    sessionid: str | None = None


@app.post("/login")
def login(req: LoginRequest):
    loader = instaloader.Instaloader()
    if req.sessionid:
        loader.context.sessionid = req.sessionid
        try:
            loader.test_login()
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
    elif req.username and req.password:
        try:
            loader.login(req.username, req.password)
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
    else:
        raise HTTPException(
            status_code=400, detail="Provide sessionid or username/password"
        )
    token = str(uuid.uuid4())
    _sessions[token] = loader
    return {"token": token}


def get_loader(token: str) -> instaloader.Instaloader:
    loader = _sessions.get(token)
    if not loader:
        raise HTTPException(status_code=401, detail="Invalid token")
    return loader


@app.get("/profile/{username}")
def profile(username: str, token: str = Query(...)):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    data = {
        "username": profile.username,
        "fullname": profile.full_name,
        "biography": profile.biography,
        "followers": profile.followers,
        "followees": profile.followees,
        "is_private": profile.is_private,
        "profile_pic_url": profile.profile_pic_url,
    }
    return data


@app.get("/posts/{username}")
def posts(username: str, token: str = Query(...), limit: int = 5):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    posts = []
    for post in profile.get_posts():
        posts.append(
            {
                "id": post.mediaid,
                "shortcode": post.shortcode,
                "url": post.url,
                "caption": post.caption,
                "date_utc": post.date_utc.isoformat(),
            }
        )
        if len(posts) >= limit:
            break
    return {"posts": posts}


@app.get("/comments/{shortcode}")
def comments(shortcode: str, token: str = Query(...), limit: int = 20):
    loader = get_loader(token)
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    comments = []
    for c in post.get_comments():
        comments.append(
            {
                "id": c.id,
                "user": c.owner.username,
                "text": c.text,
                "created_at": c.created_at_utc.isoformat(),
            }
        )
        if len(comments) >= limit:
            break
    return {"comments": comments}


@app.get("/stories/{username}")
def stories(username: str, token: str = Query(...)):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    stories = []
    for story in loader.get_stories(userids=[profile.userid]):
        for item in story.get_items():
            stories.append(
                {
                    "id": item.mediaid,
                    "url": item.url,
                    "date_utc": item.date_utc.isoformat(),
                }
            )
    return {"stories": stories}


@app.get("/followers/{username}")
def followers(username: str, token: str = Query(...), limit: int = 20):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    followers = []
    for f in profile.get_followers():
        followers.append(f.username)
        if len(followers) >= limit:
            break
    return {"followers": followers}


@app.get("/followings/{username}")
def followings(username: str, token: str = Query(...), limit: int = 20):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    followees = []
    for f in profile.get_followees():
        followees.append(f.username)
        if len(followees) >= limit:
            break
    return {"followings": followees}


@app.get("/hashtag/{tag}")
def hashtag(tag: str, token: str = Query(...), limit: int = 10):
    loader = get_loader(token)
    hashtag = instaloader.Hashtag.from_name(loader.context, tag)
    posts = []
    for post in hashtag.get_posts():
        posts.append(
            {
                "shortcode": post.shortcode,
                "url": post.url,
                "caption": post.caption,
            }
        )
        if len(posts) >= limit:
            break
    return {"hashtag": tag, "posts": posts}


@app.get("/reels/{username}")
def reels(username: str, token: str = Query(...), limit: int = 5):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    reels = []
    for post in profile.get_clips():
        reels.append(
            {
                "shortcode": post.shortcode,
                "url": post.url,
                "caption": post.caption,
            }
        )
        if len(reels) >= limit:
            break
    return {"reels": reels}


@app.get("/highlights/{username}")
def highlights(username: str, token: str = Query(...)):
    loader = get_loader(token)
    profile = instaloader.Profile.from_username(loader.context, username)
    highlights = []
    for hl in profile.get_highlights():
        for item in hl.get_items():
            highlights.append(
                {
                    "id": item.mediaid,
                    "title": hl.title,
                    "url": item.url,
                    "date_utc": item.date_utc.isoformat(),
                }
            )
    return {"highlights": highlights}
