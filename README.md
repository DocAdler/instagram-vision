# Instagram Vision

FastAPI-based Instagram scraper built with `instagrapi`. It exposes endpoints for profiles, posts, comments,
stories, reels, highlights, followers, followings and hashtag search. Authentication works via
username/password or `sessionid`. Media can be downloaded through a dedicated endpoint. The service is
ready for Railway deployment via Docker.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Use the `/login` endpoint to obtain a token before calling other routes. The token must be supplied as
`?token=...` query parameter. Media content for a post or story can be retrieved through `/download/{media_id}`.

## Docker

Build and run:

```bash
docker build -t instagram-vision .
docker run -p 8000:8000 instagram-vision
```
