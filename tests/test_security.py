from datetime import timedelta

import pytest
from jose import JWTError

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("password1234")

    assert hashed != "password1234"
    assert verify_password("password1234", hashed)
    assert not verify_password("wrong", hashed)


def test_hash_is_salted():
    assert hash_password("same") != hash_password("same")


def test_verify_password_over_72_bytes_returns_false():
    hashed = hash_password("password1234")

    assert verify_password("a" * 100, hashed) is False


def test_verify_password_malformed_hash_returns_false():
    assert verify_password("password1234", "not-a-bcrypt-hash") is False


def test_access_token_roundtrip():
    token = create_access_token(42)

    assert decode_access_token(token)["sub"] == "42"


def test_expired_access_token_rejected():
    token = create_access_token(42, expires_delta=timedelta(seconds=-1))

    with pytest.raises(JWTError):
        decode_access_token(token)
