from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import sqlite3

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
)
from pwdlib import PasswordHash

from app.core.config import settings
from app.db.database import connect_db


password_hash = PasswordHash.recommended()

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_jwt_secret() -> str:
    if not settings.jwt_secret_key:
        raise RuntimeError(
            "JWT_SECRET_KEY is missing. "
            "Add JWT_SECRET_KEY to backend/.env."
        )

    return settings.jwt_secret_key


def normalize_email(email: str) -> str:
    return email.strip().lower()


def legacy_sha256_hash(
    password: str,
) -> str:
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def is_legacy_sha256_hash(
    stored_hash: str,
) -> bool:
    if len(stored_hash) != 64:
        return False

    return all(
        character in "0123456789abcdef"
        for character in stored_hash.lower()
    )


def hash_password(
    password: str,
) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    if is_legacy_sha256_hash(stored_hash):
        return hmac.compare_digest(
            legacy_sha256_hash(password),
            stored_hash.lower(),
        )

    try:
        return password_hash.verify(
            password,
            stored_hash,
        )
    except Exception:
        return False


def create_access_token(
    email: str,
    token_version: int,
    role: str,
    token_kind: str,
) -> str:
    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": normalize_email(email),
        "ver": token_version,
        "role": str(role).strip().lower(),
        "token_kind": str(
            token_kind
        ).strip().lower(),
        "iat": now,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
    }

    return jwt.encode(
        payload,
        get_jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


def public_user(
    user: sqlite3.Row,
) -> dict[str, object]:
    return {
        "name": user["full_name"],
        "email": user["email"],
        "age": user["age"],
        "gender": user["gender"],
        "role": user["role"],
    }


def hash_reset_code(
    email: str,
    code: str,
) -> str:
    value = (
        f"{normalize_email(email)}:{code}"
    ).encode()

    return hmac.new(
        get_jwt_secret().encode(),
        value,
        hashlib.sha256,
    ).hexdigest()


def get_auth_context(
    credentials: (
        HTTPAuthorizationCredentials | None
    ) = Depends(bearer_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Invalid or expired "
            "authentication token"
        ),
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
    ):
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=[
                settings.jwt_algorithm
            ],
            issuer=settings.jwt_issuer,
            options={
                "require": [
                    "exp",
                    "iat",
                    "sub",
                    "iss",
                    "ver",
                    "role",
                    "token_kind",
                ]
            },
        )

        email = payload.get("sub")
        token_version = payload.get("ver")
        token_role = payload.get("role")
        token_kind = payload.get(
            "token_kind"
        )

        if (
            not email
            or not isinstance(email, str)
            or not isinstance(
                token_version,
                int,
            )
            or token_role
            not in {"user", "admin"}
            or token_kind
            not in {"user", "admin"}
        ):
            raise credentials_exception

    except ExpiredSignatureError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Your session has expired. "
                "Please log in again."
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from error

    except InvalidTokenError as error:
        raise credentials_exception from error

    with closing(connect_db()) as connection:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (
                normalize_email(email),
            ),
        ).fetchone()

    if not user:
        raise credentials_exception

    if (
        int(user["token_version"])
        != token_version
    ):
        raise credentials_exception

    return {
        "user": user,
        "payload": payload,
    }


def get_current_user(
    auth_context=Depends(
        get_auth_context
    ),
):
    return auth_context["user"]


def require_admin(
    auth_context=Depends(
        get_auth_context
    ),
):
    user = auth_context["user"]
    payload = auth_context["payload"]

    database_role = str(
        user["role"]
    ).strip().lower()

    token_role = str(
        payload.get("role", "")
    ).strip().lower()

    token_kind = str(
        payload.get("token_kind", "")
    ).strip().lower()

    if (
        database_role != "admin"
        or token_role != "admin"
        or token_kind != "admin"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Administrator access required"
            ),
        )

    return user