# Express Demo

This sample app makes the Node SDK integration concrete while the Python runtime and backend services are still being completed.

## Run it

```bash
npm install
npm run dev:demo
```

## Environment

- `SENTINEL_TOKEN` defaults to `sentinel_demo_token`
- `SENTINEL_INGEST_URL` defaults to `http://localhost:8000/v1/ingest/events`
- `PORT` defaults to `3001`

## Suggested local test

1. Start the demo app.
2. Hit `/`, `/health`, and `/auth/token`.
3. Once the FastAPI backend is running, point `SENTINEL_INGEST_URL` at it to start collecting runtime events.
