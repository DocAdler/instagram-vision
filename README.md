# Instagram Vision

FastAPI-based Instagram scraper built with `instagrapi`. It exposes endpoints for profiles, posts, comments,
stories, reels, highlights, followers, followings and hashtag search. Authentication works via
username/password, `sessionid`, or anonymously. Media can be downloaded through a dedicated endpoint.
The service runs on Railway via Docker and integrates well with n8n via HTTP requests. Visit the root path
`/` to see a short welcome message. Use `/login` and `/logout` to manage sessions.

## Quick start

```bash
pip install -r requirements.txt
python -m app.main
```

Use the `/login` endpoint to obtain a token before calling other routes. The token must be supplied as
`?token=...` query parameter. Media content for a post or story can be retrieved through `/download/{media_id}`.

If you omit credentials when calling `/login`, an anonymous session is created. Some endpoints may require
authentication to succeed.

### n8n integration

The API can be accessed from n8n via the HTTP Request node. Provide the token as a query parameter and parse
the JSON response for further automation. Example cURL request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username":"myuser","password":"mypass"}' \
  http://localhost:8000/login
```

Typical n8n workflow:

1. **HTTP Request** – POST to `/login` with your credentials. Store the returned token.
2. **HTTP Request** – GET `/profile/{username}?token=TOKEN` to fetch profile info.
3. **HTTP Request** – GET `/posts/{username}?token=TOKEN` to retrieve post metadata.
4. **HTTP Request** – GET `/download/{media_id}?token=TOKEN` with `Response: File` to download content.

You can conditionally switch the base URL between the Railway deployment and `http://localhost:8000` for local
testing.

## Docker

Build and run:

```bash
docker build -t instagram-vision .
docker run -p 8000:8000 -e PORT=8000 instagram-vision
```

### Environment variables

- `PORT` - port the server listens on (default `8000`). Railway sets this automatically when using the Dockerfile.
- `HOST` - interface to bind to. Defaults to `0.0.0.0`.
- `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` - optional defaults used for login if provided.

Create a `.env` file locally or export variables before starting the server. When testing locally the API
listens on `http://localhost:8000` by default. Set `PORT` and `HOST` if you need a different address. In n8n you
can switch between your Railway deployment and local instance by changing the base URL in HTTP Request nodes.
