# SentinelAPI Worker

The worker will own:

- anomaly scoring
- scheduled scans
- credential leak processing
- Slack and email dispatch
- AI triage and report generation jobs

It is scaffolded here so the job contracts are explicit while the Python runtime and legacy scanner code are still missing.

