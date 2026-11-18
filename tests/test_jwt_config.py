import time

import jwt
import pytest

from app import security
from app.security import _load_jwt_settings


@pytest.mark.parametrize(
    "algorithm",
    ["HS256", "HS384", "HS512"],
)
def test_accepts_supported_jwt_algorithms(algorithm):
    result = _load_jwt_settings(
        secret="s" * 32,
        algorithm=algorithm,
        expiry_minutes="30",
    )

    assert result == ("s" * 32, algorithm, 30)


def test_rejects_missing_jwt_secret():
    with pytest.raises(RuntimeError, match="missing"):
        _load_jwt_settings(
            secret=None,
            algorithm="HS256",
            expiry_minutes="30",
        )


def test_rejects_short_jwt_secret():
    with pytest.raises(RuntimeError, match="32 bytes"):
        _load_jwt_settings(
            secret="s" * 31,
            algorithm="HS256",
            expiry_minutes="30",
        )


@pytest.mark.parametrize(
    "algorithm",
    ["none", "RS256", "HS1024", "hs256"],
)
def test_rejects_unsupported_jwt_algorithms(algorithm):
    with pytest.raises(RuntimeError, match="JWT_ALGORITHM"):
        _load_jwt_settings(
            secret="s" * 32,
            algorithm=algorithm,
            expiry_minutes="30",
        )


@pytest.mark.parametrize(
    "expiry",
    ["abc", "", None],
)
def test_rejects_invalid_token_expiry(expiry):
    with pytest.raises(RuntimeError, match="valid integer"):
        _load_jwt_settings(
            secret="s" * 32,
            algorithm="HS256",
            expiry_minutes=expiry,
        )


@pytest.mark.parametrize(
    "expiry",
    ["0", "-1"],
)
def test_rejects_non_positive_token_expiry(expiry):
    with pytest.raises(RuntimeError, match="greater than zero"):
        _load_jwt_settings(
            secret="s" * 32,
            algorithm="HS256",
            expiry_minutes=expiry,
        )


def test_access_token_contains_correct_subject_and_expiration(
    monkeypatch,
):
    monkeypatch.setattr(
        security,
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        5,
    )

    token = security.create_access_token(user_id=123)

    payload = jwt.decode(
        token,
        security.JWT_SECRET_KEY,
        algorithms=[security.JWT_ALGORITHM],
    )

    assert payload["sub"] == "123"
    assert payload["exp"] > time.time()
    assert payload["exp"] <= time.time() + 301
