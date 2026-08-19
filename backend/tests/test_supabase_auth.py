import pytest
import jwt
from app.security.supabase_auth import verify_supabase_jwt
from app.security.exceptions import AuthenticationError

def test_verify_valid_supabase_jwt():
    secret = "test-supabase-jwt-secret-key-32-chars-long"
    payload = {
        "sub": "usr_supabase_123",
        "email": "samrat@twib.ai",
        "role": "authenticated",
        "aud": "authenticated",
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    decoded = verify_supabase_jwt(token, secret)
    assert decoded["sub"] == "usr_supabase_123"
    assert decoded["email"] == "samrat@twib.ai"

def test_verify_invalid_jwt_raises():
    with pytest.raises(AuthenticationError):
        verify_supabase_jwt("invalid.token.here", "some-secret")

def test_verify_empty_token_raises():
    with pytest.raises(AuthenticationError):
        verify_supabase_jwt("", "some-secret")
