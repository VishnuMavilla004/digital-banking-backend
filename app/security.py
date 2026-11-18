import os
from datetime import UTC, datetime, timedelta

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

password_hash = PasswordHash.recommended()


def _load_jwt_settings(
    secret: str | None,
    algorithm: str | None,
    expiry_minutes: str | None,
) -> tuple[str, str, int]:
    # Validate JWT secret.
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is missing from configuration.")

    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 bytes.")

    # Validate signing algorithm.
    supported_algorithms = {"HS256", "HS384", "HS512"}

    if algorithm not in supported_algorithms:
        raise RuntimeError("JWT_ALGORITHM must be one of HS256, HS384, or HS512.")

    # Validate token expiration.
    try:
        expiry = int(expiry_minutes)
    except (ValueError, TypeError):
        raise RuntimeError(
            "ACCESS_TOKEN_EXPIRE_MINUTES must be a valid integer."
        ) from None

    if expiry <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than zero.")

    return secret, algorithm, expiry


JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES = _load_jwt_settings(
    secret=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    expiry_minutes=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expiration = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
