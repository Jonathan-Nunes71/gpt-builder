"""Utility helpers for deduplicating content."""
from __future__ import annotations

import hashlib


def fingerprint_url(url: str) -> str:
    """Return a deterministic fingerprint for an URL."""
    return hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()


def fingerprint_content(content: str) -> str:
    """Return a deterministic fingerprint for the HTML body."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
