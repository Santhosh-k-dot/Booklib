import pytest
from datetime import timedelta
from jose import jwt

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
)

# -------------------------
# PASSWORD HASHING TESTS
# -------------------------

def test_password_hashing():
    password = "mypassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_correct():
    password = "mypassword123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_verify_password_wrong():
    password = "mypassword123"
    hashed = get_password_hash(password)

    assert verify_password("wrongpassword", hashed) is False


def test_password_longer_than_72_bytes():
    long_password = "a" * 100
    hashed = get_password_hash(long_password)

    # Should still verify correctly
    assert verify_password(long_password, hashed) is True


# -------------------------
# JWT TOKEN TESTS
# -------------------------

def test_create_access_token_default_expiry():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert isinstance(token, str)


def test_create_access_token_custom_expiry():
    data = {"sub": "testuser"}
    token = create_access_token(
        data,
        expires_delta=timedelta(minutes=5)
    )

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_verify_token_valid():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "testuser"


def test_verify_token_invalid():
    invalid_token = "this.is.not.a.valid.token"

    payload = verify_token(invalid_token)

    assert payload is None