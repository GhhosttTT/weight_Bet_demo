"""
Unit tests for Invitation model
Task 1.3: 创建 Invitation SQLAlchemy 模型
"""
import pytest
from datetime import datetime
import uuid
from app.models import Invitation, InvitationStatus


class TestInvitationModel:
    """Test suite for Invitation model"""
    
    def test_invitation_status_enum_values(self):
        """Test that InvitationStatus enum has all required values"""
        assert InvitationStatus.PENDING.value == "pending"
        assert InvitationStatus.VIEWED.value == "viewed"
        assert InvitationStatus.ACCEPTED.value == "accepted"
        assert InvitationStatus.REJECTED.value == "rejected"
        assert InvitationStatus.EXPIRED.value == "expired"
    
    def test_invitation_model_instantiation(self):
        """Test creating an Invitation instance"""
        invitation_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        inviter_id = str(uuid.uuid4())
        invitee_id = str(uuid.uuid4())
        invitee_email = "test@example.com"
        sent_at = datetime.now()
        
        invitation = Invitation(
            id=invitation_id,
            plan_id=plan_id,
            inviter_id=inviter_id,
            invitee_email=invitee_email,
            invitee_id=invitee_id,
            status=InvitationStatus.PENDING,
            sent_at=sent_at,
            viewed_at=None,
            responded_at=None
        )
        
        assert invitation.id == invitation_id
        assert invitation.plan_id == plan_id
        assert invitation.inviter_id == inviter_id
        assert invitation.invitee_email == invitee_email
        assert invitation.invitee_id == invitee_id
        assert invitation.status == InvitationStatus.PENDING
        assert invitation.sent_at == sent_at
        assert invitation.viewed_at is None
        assert invitation.responded_at is None
    
    def test_invitation_status_transitions(self):
        """Test that invitation status can be changed"""
        invitation = Invitation(
            id=str(uuid.uuid4()),
            plan_id=str(uuid.uuid4()),
            inviter_id=str(uuid.uuid4()),
            invitee_email="test@example.com",
            status=InvitationStatus.PENDING,
            sent_at=datetime.now()
        )
        
        # Test PENDING -> VIEWED
        invitation.status = InvitationStatus.VIEWED
        assert invitation.status == InvitationStatus.VIEWED
        
        # Test VIEWED -> ACCEPTED
        invitation.status = InvitationStatus.ACCEPTED
        assert invitation.status == InvitationStatus.ACCEPTED
    
    def test_invitation_timestamps(self):
        """Test that timestamps can be set and updated"""
        sent_at = datetime.now()
        invitation = Invitation(
            id=str(uuid.uuid4()),
            plan_id=str(uuid.uuid4()),
            inviter_id=str(uuid.uuid4()),
            invitee_email="test@example.com",
            status=InvitationStatus.PENDING,
            sent_at=sent_at
        )
        
        assert invitation.sent_at == sent_at
        assert invitation.viewed_at is None
        assert invitation.responded_at is None
        
        # Update timestamps
        viewed_at = datetime.now()
        responded_at = datetime.now()
        
        invitation.viewed_at = viewed_at
        invitation.responded_at = responded_at
        
        assert invitation.viewed_at == viewed_at
        assert invitation.responded_at == responded_at
    
    def test_invitation_repr(self):
        """Test the string representation of Invitation"""
        invitation_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        
        invitation = Invitation(
            id=invitation_id,
            plan_id=plan_id,
            inviter_id=str(uuid.uuid4()),
            invitee_email="test@example.com",
            status=InvitationStatus.PENDING,
            sent_at=datetime.now()
        )
        
        repr_str = repr(invitation)
        assert invitation_id in repr_str
        assert plan_id in repr_str
        assert "pending" in repr_str.lower()
    
    def test_invitation_model_has_required_attributes(self):
        """Test that Invitation model has all required attributes"""
        required_attrs = [
            'id', 'plan_id', 'inviter_id', 'invitee_email', 'invitee_id',
            'status', 'sent_at', 'viewed_at', 'responded_at',
            'plan', 'inviter', 'invitee'
        ]
        
        for attr in required_attrs:
            assert hasattr(Invitation, attr), f"Invitation model missing attribute: {attr}"
    
    def test_invitation_nullable_fields(self):
        """Test that nullable fields can be None"""
        invitation = Invitation(
            id=str(uuid.uuid4()),
            plan_id=str(uuid.uuid4()),
            inviter_id=str(uuid.uuid4()),
            invitee_email="test@example.com",
            invitee_id=None,  # Nullable
            status=InvitationStatus.PENDING,
            sent_at=datetime.now(),
            viewed_at=None,  # Nullable
            responded_at=None  # Nullable
        )
        
        assert invitation.invitee_id is None
        assert invitation.viewed_at is None
        assert invitation.responded_at is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
