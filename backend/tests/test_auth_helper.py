import pytest
import jwt
from datetime import datetime, timedelta, timezone
import os

# Ensure SECRET_KEY is set before importing
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars-minimum"

from services.auth_helper import (
    create_access_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE,
)


class TestCreateAccessToken:
    """Tests for create_access_token function"""

    def test_returns_valid_jwt_string(self):
        """create_access_token should return a valid JWT string"""
        data = {"sub": "1", "role": "admin"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

    def test_token_contains_correct_claims(self):
        """Token should contain the correct sub and role claims"""
        data = {"sub": "42", "role": "manager"}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert decoded["sub"] == "42"
        assert decoded["role"] == "manager"

    def test_token_contains_expiration(self):
        """Token should contain an expiration time"""
        data = {"sub": "1", "role": "viewer"}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in decoded
        # Expiration should be in the future
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp_time > now

    def test_token_expiration_is_correct(self):
        """Token expiration should match ACCESS_TOKEN_EXPIRE"""
        data = {"sub": "1", "role": "admin"}
        before = datetime.now(timezone.utc)
        token = create_access_token(data)
        after = datetime.now(timezone.utc)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)

        # Expiration should be approximately now + ACCESS_TOKEN_EXPIRE
        expected_min = before + ACCESS_TOKEN_EXPIRE
        expected_max = after + ACCESS_TOKEN_EXPIRE

        assert expected_min <= exp_time <= expected_max


class TestDecodeAccessToken:
    """Tests for decode_access_token function"""

    def test_decodes_valid_token(self):
        """decode_access_token should correctly decode a valid token"""
        data = {"sub": "123", "role": "admin"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded["sub"] == "123"
        assert decoded["role"] == "admin"
        assert "exp" in decoded

    def test_raises_on_expired_token(self):
        """decode_access_token should raise on expired token"""
        # Create an already-expired token
        data = {"sub": "1", "role": "viewer"}
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        to_encode.update({"exp": expire})
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(expired_token)

    def test_raises_on_invalid_token(self):
        """decode_access_token should raise on invalid/tampered token"""
        invalid_token = "invalid.token.string"

        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(invalid_token)

    def test_raises_on_tampered_token(self):
        """decode_access_token should raise on tampered token"""
        data = {"sub": "1", "role": "admin"}
        token = create_access_token(data)

        # Tamper with the token by modifying a character
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(tampered)

    def test_raises_on_wrong_secret(self):
        """decode_access_token should raise when token signed with different secret"""
        data = {"sub": "1", "role": "admin"}
        wrong_secret = "wrong-secret-key-12345678901234567890"
        token = jwt.encode(
            {**data, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            wrong_secret,
            algorithm=ALGORITHM
        )

        with pytest.raises(jwt.InvalidSignatureError):
            decode_access_token(token)

    def test_token_without_sub_claim(self):
        """Token without sub claim should still decode but payload will not have sub"""
        data = {"role": "admin"}  # No sub claim
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert "sub" not in decoded
        assert decoded["role"] == "admin"


class TestSecretKeyValidation:
    """Tests for SECRET_KEY validation"""

    def test_secret_key_is_set(self):
        """SECRET_KEY should be set from environment"""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_algorithm_is_hs256(self):
        """ALGORITHM should be HS256"""
        assert ALGORITHM == "HS256"
