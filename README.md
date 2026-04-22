# SentinelAPI

SentinelAPI is a developer-first security monitoring platform for APIs and supporting infrastructure.

This repo is now structured as the foundation for the private beta:

- `apps/web` contains the marketing site, docs, beta flow, and dashboard shell.
- `apps/api` contains the FastAPI service scaffold and HTTP contracts.
- `apps/worker` contains the background worker scaffold for anomaly detection, scans, and notifications.
- `packages/sdk-node` contains the first Node SDK client and Express middleware.
- `packages/sdk-python` contains the Python SDK package scaffold for FastAPI and Flask.
- `examples/express-demo` contains a runnable Express sample wired to the Node SDK.

## Current status

- The web app is runnable with Node and npm.
- The API, worker, and Python SDK are scaffolded but not runnable on this machine because Python is not installed or not on PATH.
- The legacy scanner and monitoring code referenced in the business plan still needs to be restored and wired into the adapter layer before the full security feature set is complete.

## Quick start

```bash
npm install
npm run dev:web
```

Then open `http://localhost:3000`.

To run the local Express sample:

```bash
npm run dev:demo
```

Copy `.env.example` to `.env.local` or your deployment environment before wiring waitlist persistence, auth, billing, or outbound integrations.
