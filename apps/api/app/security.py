from __future__ import annotations

import hmac
import json
import time
from collections import defaultdict, deque
from hashlib import sha256
from typing import Deque

from fastapi import HTTPException, Request, status

from .settings import settings


_request_windows: dict[str, Deque[float]] = defaultdict(deque)


def validate_org_token(org_token: str) -> str:
    if org_token in settings.dev_org_tokens:
        return org_token

    if len(org_token) < 12:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization token is too short.",
        )

    if not (
        org_token.startswith("org_")
        or org_token.startswith("sentinel_")
        or org_token.startswith("sk_")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization token format is invalid.",
        )

    return org_token


def enforce_rate_limit(client_key: str) -> None:
    now = time.time()
    window = _request_windows[client_key]
    threshold = now - settings.rate_limit_window_seconds

    while window and window[0] < threshold:
        window.popleft()

    if len(window) >= settings.rate_limit_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
        )

    window.append(now)


def attach_security_headers(request: Request, response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none';"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"


def verify_github_signature(body: bytes, signature_header: str | None) -> None:
    if not settings.github_webhook_secret:
        return

    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing GitHub signature.",
        )

    expected = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        body,
        sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid GitHub signature.",
        )


def verify_stripe_signature(body: bytes, signature_header: str | None) -> None:
    if not settings.stripe_webhook_secret:
        return

    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Stripe signature.",
        )

    timestamp = None
    signature = None
    for part in signature_header.split(","):
      key, _, value = part.partition("=")
      if key == "t":
          timestamp = value
      if key == "v1":
          signature = value

    if not timestamp or not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Stripe signature.",
        )

    signed_payload = f"{timestamp}.{body.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(
        settings.stripe_webhook_secret.encode("utf-8"),
        signed_payload,
        sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Stripe signature.",
        )


def parse_json_body(body: bytes) -> dict:
    try:
        parsed = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be valid JSON.",
        ) from error

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be a JSON object.",
        )

    return parsed
