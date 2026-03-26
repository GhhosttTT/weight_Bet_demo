"""
Compatibility shim: re-export security utilities from app.utils.security
This allows legacy imports like `from app.core.security import create_access_token` to continue working.
"""
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]

