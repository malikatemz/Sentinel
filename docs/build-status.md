# Build Status

## Ready now

- Next.js marketing site
- Pricing, docs, beta, and dashboard shell routes
- Waitlist API route with optional webhook forwarding
- Node SDK scaffold with Express middleware and event ingestion client
- FastAPI, worker, and Python SDK contracts

## Blockers to full product completion

1. Python runtime is missing from this machine, so the FastAPI service, worker, and Python SDK cannot be executed or tested locally yet.
2. The business plan depends on existing port scanning and monitoring logic that is not present in this workspace.
3. Supabase, Clerk, Stripe, Slack, SendGrid, GitHub, and OpenAI credentials are not configured yet.

## Next implementation steps

1. Install Python 3.12+ and pip.
2. Restore the legacy scanner and detector code into the monorepo.
3. Implement the FastAPI ingestion and worker jobs against the documented contracts.
4. Replace the placeholder dashboard data with live Supabase-backed data.

