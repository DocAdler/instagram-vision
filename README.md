# Instagram Vision

FastAPI-based Instagram scraper using Instaloader. Provides JSON responses for profiles, posts, comments, stories, reels, highlights, followers and followings, and hashtag search. Supports authentication via username/password or sessionid. Suitable for deployment on Railway via Docker.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Use the `/login` endpoint to obtain a token before accessing other endpoints.

## Docker

Build and run:

```bash
docker build -t instagram-vision .
docker run -p 8000:8000 instagram-vision
```
