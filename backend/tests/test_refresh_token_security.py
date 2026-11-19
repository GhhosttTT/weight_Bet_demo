"""服务端 Refresh Token 轮换与吊销测试。"""

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.user import Gender, User
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService
from app.utils.security import hash_password


@pytest.fixture()
def auth_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    db.add(User(
        id="refresh-user-001", email="refresh@example.com", password_hash=hash_password("secret123"),
        nickname="Refresh User", gender=Gender.OTHER, age=30, height=170,
        current_weight=70, target_weight=65,
    ))
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_refresh_token_is_rotated_and_old_token_cannot_be_replayed(auth_db):
    first = AuthService.login(auth_db, LoginRequest(email="refresh@example.com", password="secret123"))
    second = AuthService.refresh_token(auth_db, first.refresh_token)

    assert second.refresh_token != first.refresh_token
    with pytest.raises(HTTPException) as error:
        AuthService.refresh_token(auth_db, first.refresh_token)
    assert error.value.status_code == 401


def test_logout_revokes_refresh_token(auth_db):
    result = AuthService.login(auth_db, LoginRequest(email="refresh@example.com", password="secret123"))
    AuthService.revoke_refresh_token(auth_db, result.refresh_token)

    with pytest.raises(HTTPException) as error:
        AuthService.refresh_token(auth_db, result.refresh_token)
    assert error.value.status_code == 401
