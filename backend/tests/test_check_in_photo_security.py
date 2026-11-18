from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.check_ins import UPLOAD_ROOT, _matches_image_signature
from app.database import Base, get_db
from app.main import app
from app.models import BettingPlan, CheckIn, Gender, PlanStatus, ReviewStatus, User
from app.utils.security import create_access_token, hash_password


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def photo_context(tmp_path, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr("app.api.check_ins.UPLOAD_ROOT", tmp_path)

    db = Session()
    users = [
        User(id="photo-owner", email="owner@example.com", password_hash=hash_password("secret"), nickname="Owner", gender=Gender.OTHER, age=30, height=170, current_weight=70),
        User(id="photo-participant", email="participant@example.com", password_hash=hash_password("secret"), nickname="Participant", gender=Gender.OTHER, age=30, height=170, current_weight=70),
        User(id="photo-outsider", email="outsider@example.com", password_hash=hash_password("secret"), nickname="Outsider", gender=Gender.OTHER, age=30, height=170, current_weight=70),
    ]
    plan = BettingPlan(
        id="photo-plan", creator_id="photo-owner", participant_id="photo-participant", status=PlanStatus.ACTIVE,
        bet_amount=10, start_date=datetime.utcnow() - timedelta(days=2), end_date=datetime.utcnow() + timedelta(days=2),
        creator_initial_weight=80, creator_target_weight=75, creator_target_weight_loss=5,
        participant_initial_weight=80, participant_target_weight=75, participant_target_weight_loss=5,
    )
    check_in = CheckIn(
        id="photo-check-in", user_id="photo-owner", plan_id=plan.id, weight=79,
        check_in_date=datetime.utcnow().date(), photo_url="/uploads/checkins/photo.jpg", review_status=ReviewStatus.APPROVED,
    )
    db.add_all(users + [plan, check_in])
    db.commit()
    db.close()
    (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8\xffphoto")

    client = TestClient(app)
    yield client
    client.close()
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def headers(user_id):
    return {"Authorization": f"Bearer {create_access_token({'sub': user_id})}"}


def test_photo_file_requires_plan_access(photo_context):
    client = photo_context
    assert client.get("/api/check-ins/photo-check-in/photo", headers=headers("photo-owner")).status_code == 200
    assert client.get("/api/check-ins/photo-check-in/photo", headers=headers("photo-participant")).status_code == 200
    assert client.get("/api/check-ins/photo-check-in/photo", headers=headers("photo-outsider")).status_code == 403


def test_upload_signature_rejects_content_type_spoofing():
    assert _matches_image_signature(b"\xff\xd8\xff...", "image/jpeg")
    assert _matches_image_signature(b"<script>alert(1)</script>", "image/jpeg") is False
    assert _matches_image_signature(b"\x89PNG\r\n\x1a\n...", "image/png")
