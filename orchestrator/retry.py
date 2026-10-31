"""`/retry`: the owner clears an Issue's Builder failures and auto-stop by commenting on it."""

from __future__ import annotations

import re

RETRY_WORDS = re.compile(r"(^|\s)(/retry|重试)(\s|$)", re.I)


def is_retry(comment: dict, owner: str) -> bool:
    """A plain owner comment asking to retry. Agents also post as the owner, but always with a marker."""
    body = comment.get("body") or ""
    return (
        (comment.get("user") or {}).get("login") == owner
        and "<!-- venture-" not in body
        and bool(RETRY_WORDS.search(body))
    )


def since_last_retry(comments: list[dict], owner: str) -> list[dict]:
    """Comments after the owner's latest /retry; everything if there is none."""
    retries = [c.get("created_at") or "" for c in comments if is_retry(c, owner)]
    if not retries:
        return comments
    latest = max(retries)
    return [c for c in comments if (c.get("created_at") or "") > latest]
