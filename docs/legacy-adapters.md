# Legacy Adapter Contracts

The business plan assumes existing security tooling will be restored and integrated here instead of rewritten from scratch.

## Required adapters

- `PortScanner.scan_target(target)` returns open ports and risk summaries for an internet-facing host.
- `TrafficDetector.score_event(event)` returns an anomaly score and optional reasons for a single runtime event.
- `TrafficDetector.build_baseline(events)` recalculates the rolling baseline snapshot for an endpoint.
- `SecretDetector.scan_github_event(payload)` returns any suspected credential leaks found in GitHub webhook payloads.

## Integration rule

The restored code should only be wired into the app through the adapter interfaces in `apps/api/app/adapters.py`. That keeps the API and worker code stable even if the legacy implementation changes.

