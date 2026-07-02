from datetime import UTC, datetime, timedelta
from hashlib import sha256
from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

TOKEN_TTL_MINUTES = 60
TOKEN_SECRET = "local-development-secret"
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, now: datetime | None = None) -> str:
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=TOKEN_TTL_MINUTES)
    body = f"{subject}:{int(expires_at.timestamp())}"
    signature = sha256(f"{body}:{TOKEN_SECRET}".encode()).hexdigest()
    return f"{body}:{signature}"


def verify_access_token(token: str, now: datetime | None = None) -> str | None:
    parts = token.split(":")
    if len(parts) != 3:
        return None

    subject, expires_raw, signature = parts
    body = f"{subject}:{expires_raw}"
    expected = sha256(f"{body}:{TOKEN_SECRET}".encode()).hexdigest()
    if not compare_digest(signature, expected):
        return None

    try:
        expires_at = datetime.fromtimestamp(int(expires_raw), tz=UTC)
    except ValueError:
        return None

    if expires_at <= (now or datetime.now(UTC)):
        return None
    return subject


def require_subject(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    subject = verify_access_token(credentials.credentials)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )
    return subject
