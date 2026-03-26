"""
Test script to verify Invitation model can be instantiated
"""
from app.models import Invitation, InvitationStatus
from datetime import datetime
import uuid


def test_invitation_instance():
    """Test creating an Invitation instance"""
    print("Testing Invitation model instantiation...")
    
    # Create a test invitation instance
    invitation = Invitation(
        id=str(uuid.uuid4()),
        plan_id=str(uuid.uuid4()),
        inviter_id=str(uuid.uuid4()),
        invitee_email="test@example.com",
        invitee_id=str(uuid.uuid4()),
        status=InvitationStatus.PENDING,
        sent_at=datetime.now(),
        viewed_at=None,
        responded_at=None
    )
    
    # Verify attributes
    print(f"✓ Created invitation with ID: {invitation.id}")
    print(f"✓ Status: {invitation.status}")
    print(f"✓ Invitee email: {invitation.invitee_email}")
    print(f"✓ Sent at: {invitation.sent_at}")
    print(f"✓ Viewed at: {invitation.viewed_at}")
    print(f"✓ Responded at: {invitation.responded_at}")
    
    # Test status enum values
    print("\nTesting status transitions:")
    invitation.status = InvitationStatus.VIEWED
    print(f"✓ Changed status to: {invitation.status}")
    
    invitation.status = InvitationStatus.ACCEPTED
    print(f"✓ Changed status to: {invitation.status}")
    
    print("\n✅ Invitation model instantiation test passed!")
    return invitation


if __name__ == "__main__":
    test_invitation_instance()
