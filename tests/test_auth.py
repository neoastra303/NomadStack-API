import pytest
from jose import jwt

from app.api.endpoints.auth import create_access_token
from app.core.config import get_settings

settings = get_settings()


def test_create_access_token():
    token = create_access_token({"sub": "1"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "1"
    assert "exp" in payload


def test_token_contains_user_id():
    token = create_access_token({"sub": "42"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"


def test_token_rejects_wrong_secret():
    token = create_access_token({"sub": "1"})
    with pytest.raises(Exception):
        jwt.decode(token, "wrong-secret", algorithms=[settings.ALGORITHM])
