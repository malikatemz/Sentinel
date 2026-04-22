# Supabase Local Setup

The repo is already initialized for local Supabase development.

## What is wired

- `supabase/config.toml` created with local ports and auth defaults
- `supabase/migrations/0001_initial.sql` for the SentinelAPI schema
- `supabase/seed.sql` for demo org, endpoint, and alert data
- root npm scripts for `supabase:start`, `supabase:stop`, `supabase:status`, and `supabase:reset`

## Commands

```bash
npm run supabase:start
npm run supabase:status
npm run supabase:reset
npm run supabase:stop
```

## Current blocker on this machine

`supabase start` currently fails because Docker Desktop is not installed or not running. The CLI is working through `npx`, and once Docker is available the local stack should be able to start using the existing config and migrations.

## Expected local ports

- Studio: `http://127.0.0.1:54323`
- API: `http://127.0.0.1:54321`
- Postgres: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
