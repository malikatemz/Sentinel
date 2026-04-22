from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


@dataclass
class AuthContext:
    org_key: str
    token_name: str


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def slugify_org_name(name: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in name.strip())
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts)[:64] or "org"


def generate_api_token() -> str:
    return f"sentinel_{secrets.token_urlsafe(32)}"
