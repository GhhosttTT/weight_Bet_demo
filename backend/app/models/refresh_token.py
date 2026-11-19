"""服务端可撤销的 Refresh Token 会话。"""
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True, index=True)
    replaced_by_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def is_active(self, now: datetime = None) -> bool:
        now = now or datetime.utcnow()
        expires_at = self.expires_at
        if expires_at is not None and expires_at.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return self.revoked_at is None and expires_at is not None and expires_at > now
