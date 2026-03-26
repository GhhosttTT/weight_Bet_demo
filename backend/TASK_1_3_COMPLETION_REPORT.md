# Task 1.3 Completion Report: 创建 Invitation SQLAlchemy 模型

## Task Summary
**Task ID:** 1.3  
**Task Name:** 创建 Invitation SQLAlchemy 模型  
**Status:** ✅ COMPLETED  
**Date:** 2024-03-24

## Requirements Addressed
- ✅ Requirement 1.1: Invitation model with all required fields
- ✅ Requirement 10.1: sent_at timestamp field
- ✅ Requirement 10.2: viewed_at timestamp field  
- ✅ Requirement 10.3: responded_at timestamp field

## Implementation Details

### 1. InvitationStatus Enum
Created enum with 5 states:
- `PENDING`: Initial state when invitation is sent
- `VIEWED`: When invitee views the invitation
- `ACCEPTED`: When invitee accepts the invitation
- `REJECTED`: When invitee rejects the invitation
- `EXPIRED`: When invitation expires without response

**Location:** `backend/app/models/invitation.py`

```python
class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
```

### 2. Invitation Model
Created SQLAlchemy model with all required fields:

**Primary Key:**
- `id`: String(36) - UUID primary key

**Foreign Keys:**
- `plan_id`: String(36) → betting_plans.id (unique, not null)
- `inviter_id`: String(36) → users.id (not null)
- `invitee_id`: String(36) → users.id (nullable)

**Data Fields:**
- `invitee_email`: String(255) - Email address of invitee
- `status`: Enum(InvitationStatus) - Current invitation status

**Timestamps:**
- `sent_at`: DateTime(timezone=True) - When invitation was sent (auto-set)
- `viewed_at`: DateTime(timezone=True) - When invitation was viewed (nullable)
- `responded_at`: DateTime(timezone=True) - When invitation was responded to (nullable)

### 3. Relationship Mappings
Configured three relationships:

```python
# Relationship to BettingPlan
plan = relationship("BettingPlan", back_populates="invitation")

# Relationship to User (inviter)
inviter = relationship("User", foreign_keys=[inviter_id])

# Relationship to User (invitee)
invitee = relationship("User", foreign_keys=[invitee_id])
```

### 4. Database Constraints
Implemented validation rules:

**Unique Constraint:**
- One invitation per plan (plan_id is unique)

**Check Constraint:**
- Status must be one of: pending, viewed, accepted, rejected, expired

**Indexes:**
- Primary key index on `id`
- Index on `plan_id`
- Index on `inviter_id`
- Index on `invitee_email` (for friend search)
- Index on `invitee_id`
- Index on `status` (for filtering)

### 5. Integration with Existing Models

**BettingPlan Model:**
Added relationship in `backend/app/models/betting_plan.py`:
```python
invitation = relationship("Invitation", back_populates="plan", uselist=False)
```

**Models Export:**
Updated `backend/app/models/__init__.py` to export:
- `Invitation` class
- `InvitationStatus` enum

## Database Migration
Migration file already exists: `backend/alembic/versions/001_create_invitations_table.py`

The migration includes:
- ✅ Create invitations table with all columns
- ✅ Create all foreign key constraints
- ✅ Create unique constraint on plan_id
- ✅ Create check constraint on status
- ✅ Create all required indexes
- ✅ Add abandoned_by, abandoned_at, expiry_checked_at to betting_plans
- ✅ Add 'expired' value to PlanStatus enum

## Verification Results

### Model Structure Verification
All required components verified:
- ✅ InvitationStatus enum with 5 values
- ✅ All 9 required columns present
- ✅ All 3 relationships configured
- ✅ Unique constraint on plan_id
- ✅ Check constraint on status
- ✅ All 6 indexes created

### Instantiation Test
Successfully tested:
- ✅ Creating Invitation instances
- ✅ Setting all attributes
- ✅ Status transitions
- ✅ Enum value validation

### Import Test
Verified:
- ✅ Model can be imported from app.models
- ✅ InvitationStatus enum accessible
- ✅ All attributes accessible via dir()

## Files Modified/Created

### Existing Files (Already Complete)
1. `backend/app/models/invitation.py` - Invitation model definition
2. `backend/app/models/__init__.py` - Model exports
3. `backend/app/models/betting_plan.py` - Added invitation relationship
4. `backend/alembic/versions/001_create_invitations_table.py` - Database migration

### Verification Files Created
1. `backend/verify_invitation_model_task.py` - Comprehensive verification script
2. `backend/test_invitation_model_instance.py` - Instantiation test
3. `backend/TASK_1_3_COMPLETION_REPORT.md` - This report

## Validation Rules (Application Layer)
The following validation rules should be implemented in the service layer:

1. **Email Format Validation:**
   - invitee_email must match valid email regex pattern

2. **Status Transition Rules:**
   - PENDING → VIEWED (when invitee views)
   - PENDING → ACCEPTED (when invitee accepts)
   - PENDING → REJECTED (when invitee rejects)
   - PENDING → EXPIRED (when invitation times out)
   - VIEWED → ACCEPTED (when invitee accepts after viewing)
   - VIEWED → REJECTED (when invitee rejects after viewing)

3. **Timestamp Ordering:**
   - viewed_at must be >= sent_at (if not null)
   - responded_at must be >= viewed_at (if viewed_at not null)
   - responded_at must be >= sent_at

4. **Business Rules:**
   - Cannot invite self (inviter_id ≠ invitee_id)
   - One invitation per plan (enforced by unique constraint)
   - Plan must be in PENDING status to send invitation

## Next Steps
The following tasks depend on this model:

- **Task 1.4:** Add database index optimization
- **Task 2.3:** Implement InvitationService.create_invitation
- **Task 2.4:** Implement InvitationService query methods
- **Task 6.2:** Implement POST /api/betting-plans/{plan_id}/invite endpoint
- **Task 6.3:** Implement GET /api/invitations endpoint

## Conclusion
✅ **Task 1.3 is COMPLETE**

The Invitation SQLAlchemy model has been successfully created with:
- Complete data model definition
- All required fields and relationships
- Proper constraints and indexes
- Database migration ready
- Full integration with existing models
- Comprehensive verification

The model is ready for use in the service layer implementation.
