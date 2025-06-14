# Instagram Vision

FastAPI-based Instagram scraper built with `instagrapi`. It exposes endpoints for profiles, posts, comments,
stories, reels, highlights, followers, followings and hashtag search. Authentication works via
username/password, `sessionid`, or anonymously. Media can be downloaded through a dedicated endpoint.
The service is ready for Railway deployment via Docker and integrates well with n8n via HTTP requests.

Visit the root path `/` to see a short welcome message. Use `/login` and `/logout` to manage sessions.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
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

## Docker

Build and run:

```bash
docker build -t instagram-vision .
docker run -p 8000:8000 instagram-vision
```

## Responsible use

Ensure you follow Instagram's Terms of Service and comply with local laws when scraping or downloading content.

## License

Released under the [MIT License](LICENSE).
