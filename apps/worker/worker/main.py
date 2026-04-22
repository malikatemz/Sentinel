from dataclasses import dataclass
from typing import Literal


@dataclass
class Job:
    kind: Literal["baseline", "scan", "credential", "notify", "report"]
    org_id: str
    payload: dict


def handle_job(job: Job) -> dict[str, str]:
    return {
        "status": "placeholder",
        "kind": job.kind,
        "message": "Implement queue wiring and legacy detector adapters here.",
    }

