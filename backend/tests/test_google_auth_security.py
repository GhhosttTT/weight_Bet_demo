"""Google OIDC 登录安全边界测试。"""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base
from app.models.balance import Balance
from app.models.user import Gender, User
from app.services.auth_service import AuthService


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def google_config(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_IDS", "web-client-id,android-client-id")


def google_claims(**overrides):
    claims = {
        "iss": "https://accounts.google.com",
        "aud": "web-client-id",
        "sub": "google-sub-001",
        "email": "User@Example.com",
        "email_verified": True,
        "name": "Google User",
    }
    claims.update(overrides)
    return claims


def test_google_login_rejects_unconfigured_provider(db_session, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_IDS", "")

    with pytest.raises(HTTPException) as error:
        AuthService.google_login(db_session, "token")

    assert error.value.status_code == 503


def test_google_login_passes_all_configured_audiences_and_creates_user(
    db_session, google_config
):
    with patch(
        "app.services.auth_service.id_token.verify_oauth2_token",
        return_value=google_claims(),
    ) as verifier:
        result = AuthService.google_login(db_session, "valid-token")

    verifier.assert_called_once()
    assert verifier.call_args[0][2] == ["web-client-id", "android-client-id"]
    user = db_session.query(User).one()
    assert user.email == "user@example.com"
    assert user.google_subject == "google-sub-001"
    assert db_session.query(Balance).filter_by(user_id=user.id).one()
    assert result.user_id == user.id


@pytest.mark.parametrize(
    "claims",
    [
        google_claims(email_verified=False),
        google_claims(email_verified=None),
        google_claims(iss="https://evil.example.com"),
        google_claims(sub=""),
        google_claims(email=""),
    ],
)
def test_google_login_rejects_untrusted_identity_claims(
    db_session, google_config, claims
):
    with patch(
        "app.services.auth_service.id_token.verify_oauth2_token",
        return_value=claims,
    ):
        with pytest.raises(HTTPException) as error:
            AuthService.google_login(db_session, "token")

    assert error.value.status_code == 400
    assert db_session.query(User).count() == 0


def test_google_login_binds_verified_email_to_existing_user(db_session, google_config):
    user = User(
        id="local-user-001",
        email="user@example.com",
        password_hash="local-password-hash",
        nickname="Local User",
        gender=Gender.OTHER,
        age=30,
        height=170,
        current_weight=70,
    )
    db_session.add(user)
    db_session.commit()

    with patch(
        "app.services.auth_service.id_token.verify_oauth2_token",
        return_value=google_claims(),
    ):
        result = AuthService.google_login(db_session, "token")

    db_session.refresh(user)
    assert result.user_id == user.id
    assert user.google_subject == "google-sub-001"
    assert db_session.query(User).count() == 1


def test_google_login_rejects_subject_mismatch_for_existing_email(
    db_session, google_config
):
    user = User(
        id="local-user-002",
        email="user@example.com",
        password_hash="local-password-hash",
        nickname="Local User",
        gender=Gender.OTHER,
        age=30,
        height=170,
        current_weight=70,
        google_subject="another-google-sub",
    )
    db_session.add(user)
    db_session.commit()

    with patch(
        "app.services.auth_service.id_token.verify_oauth2_token",
        return_value=google_claims(),
    ):
        with pytest.raises(HTTPException) as error:
            AuthService.google_login(db_session, "token")

    assert error.value.status_code == 409


def test_google_login_rejects_mismatched_nonce(db_session, google_config):
    with patch(
        "app.services.auth_service.id_token.verify_oauth2_token",
        return_value=google_claims(nonce="server-issued-nonce"),
    ):
        with pytest.raises(HTTPException) as error:
            AuthService.google_login(db_session, "token", nonce="different-nonce-value")

    assert error.value.status_code == 400
    assert db_session.query(User).count() == 0
