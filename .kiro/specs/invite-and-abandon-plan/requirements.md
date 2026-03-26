# Requirements Document

## Introduction

本文档定义了减肥对赌应用中的好友邀请和计划放弃功能。该功能允许用户邀请好友参与减肥计划，并在不同状态下放弃计划，同时正确处理赌金的冻结和退还逻辑。

## Glossary

- **User**: 使用减肥对赌应用的用户
- **Plan_Creator**: 创建减肥计划的用户
- **Plan_Participant**: 被邀请参与减肥计划的用户
- **Betting_Plan**: 减肥对赌计划，包含目标、时间范围和赌金信息
- **Invitation_System**: 处理好友邀请的系统组件
- **Friend_Search_Service**: 根据邮箱搜索好友信息的服务
- **Plan_Status_Manager**: 管理计划状态转换的系统组件
- **Fund_Manager**: 处理赌金冻结、退还和分配的系统组件
- **Notification_Service**: 发送通知给用户的服务
- **Stake_Amount**: 用户为参与计划而冻结的赌金金额

## Requirements

### Requirement 1: 邀请好友参与计划

**User Story:** 作为计划创建者，我想邀请好友参与我的减肥计划，以便我们可以一起对赌减肥。

#### Acceptance Criteria

1. WHEN THE Plan_Creator clicks the invite button, THE Invitation_System SHALL display an invitation interface
2. THE Invitation_System SHALL allow THE Plan_Creator to input a friend's email address
3. WHEN THE Plan_Creator clicks the search icon, THE Friend_Search_Service SHALL search for the friend by email address
4. WHEN a friend is found, THE Friend_Search_Service SHALL display the friend's name and age
5. WHEN THE Plan_Creator confirms the invitation, THE Invitation_System SHALL send an invitation to THE Plan_Participant
6. WHEN an invitation is sent, THE Notification_Service SHALL notify THE Plan_Participant
7. THE Invitation_System SHALL allow THE Plan_Participant to view the plan details
8. THE Invitation_System SHALL allow THE Plan_Participant to accept or reject the invitation

### Requirement 2: 好友搜索功能

**User Story:** 作为计划创建者，我想通过邮箱搜索好友，以便确认我邀请的是正确的人。

#### Acceptance Criteria

1. WHEN THE Plan_Creator enters an email address, THE Friend_Search_Service SHALL validate the email format
2. IF the email format is invalid, THEN THE Friend_Search_Service SHALL display an error message
3. WHEN a valid email is submitted, THE Friend_Search_Service SHALL query the user database
4. WHEN a matching user is found, THE Friend_Search_Service SHALL return the user's name and age
5. IF no matching user is found, THEN THE Friend_Search_Service SHALL display a "user not found" message

### Requirement 3: 计划状态管理

**User Story:** 作为系统管理员，我想系统能够正确管理计划的各种状态，以便准确跟踪计划的生命周期。

#### Acceptance Criteria

1. THE Plan_Status_Manager SHALL support the following states: pending, active, completed, cancelled, rejected, expired
2. WHEN a plan is created, THE Plan_Status_Manager SHALL set the initial status to pending
3. WHEN THE Plan_Participant accepts an invitation, THE Plan_Status_Manager SHALL change the status from pending to active
4. WHEN THE Plan_Participant rejects an invitation, THE Plan_Status_Manager SHALL change the status from pending to rejected
5. WHEN a plan reaches its end date, THE Plan_Status_Manager SHALL evaluate the plan completion
6. IF a plan reaches its end date and is not completed, THEN THE Plan_Status_Manager SHALL change the status to expired
7. WHEN a user abandons a plan, THE Plan_Status_Manager SHALL change the status to cancelled

### Requirement 4: 计划过期处理

**User Story:** 作为用户，我想系统能够自动标记过期的计划，以便我知道哪些计划已经超过了截止日期。

#### Acceptance Criteria

1. WHEN a plan's end date is reached, THE Plan_Status_Manager SHALL check if the plan is completed
2. IF the plan status is active and the end date has passed, THEN THE Plan_Status_Manager SHALL change the status to expired
3. WHEN a plan status changes to expired, THE Notification_Service SHALL notify both participants
4. THE Plan_Status_Manager SHALL run the expiration check at least once per day

### Requirement 5: 放弃待接受状态的计划

**User Story:** 作为用户，我想在计划还未开始时能够放弃计划，以便在改变主意时取回我的赌金。

#### Acceptance Criteria

1. WHILE a plan status is pending, THE Betting_Plan SHALL display an abandon button
2. WHEN THE Plan_Creator abandons a pending plan, THE Fund_Manager SHALL unfreeze THE Plan_Creator's Stake_Amount
3. WHEN THE Plan_Creator abandons a pending plan, THE Plan_Status_Manager SHALL change the status to cancelled
4. WHEN THE Plan_Participant rejects an invitation, THE Fund_Manager SHALL unfreeze THE Plan_Creator's Stake_Amount
5. WHEN THE Plan_Participant rejects an invitation, THE Plan_Status_Manager SHALL change the status to rejected
6. WHEN a pending plan is abandoned or rejected, THE Notification_Service SHALL notify the other participant

### Requirement 6: 放弃进行中的计划

**User Story:** 作为用户，我想在计划进行中时能够放弃计划，但我理解这意味着我将失去赌金。

#### Acceptance Criteria

1. WHILE a plan status is active, THE Betting_Plan SHALL display an abandon button with a warning message
2. WHEN a User abandons an active plan, THE Plan_Status_Manager SHALL mark that User as the losing party
3. WHEN a User abandons an active plan, THE Fund_Manager SHALL transfer the abandoning User's Stake_Amount to the other participant
4. WHEN a User abandons an active plan, THE Fund_Manager SHALL unfreeze and transfer the other participant's Stake_Amount to that participant
5. WHEN an active plan is abandoned, THE Plan_Status_Manager SHALL change the status to cancelled
6. WHEN an active plan is abandoned, THE Notification_Service SHALL notify the winning participant
7. THE Betting_Plan SHALL require confirmation before processing an abandon action on an active plan

### Requirement 7: 资金处理的原子性

**User Story:** 作为系统管理员，我想确保所有资金操作都是原子性的，以便避免资金丢失或重复处理。

#### Acceptance Criteria

1. WHEN THE Fund_Manager processes any fund operation, THE Fund_Manager SHALL use database transactions
2. IF a fund operation fails, THEN THE Fund_Manager SHALL roll back all related changes
3. WHEN a fund operation completes, THE Fund_Manager SHALL log the transaction details
4. THE Fund_Manager SHALL ensure that the total amount of frozen and transferred funds equals the original Stake_Amount
5. IF a fund operation is interrupted, THEN THE Fund_Manager SHALL maintain data consistency

### Requirement 8: 邀请通知内容

**User Story:** 作为被邀请的用户，我想收到包含完整计划信息的通知，以便我能够做出明智的决定。

#### Acceptance Criteria

1. WHEN an invitation is sent, THE Notification_Service SHALL include the Plan_Creator's name in the notification
2. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's target weight loss goal
3. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's duration
4. WHEN an invitation is sent, THE Notification_Service SHALL include the Stake_Amount
5. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's start and end dates
6. THE Notification_Service SHALL provide a direct link to view the full plan details

### Requirement 9: 单元测试覆盖

**User Story:** 作为开发者，我想为邀请和放弃功能编写全面的单元测试，以便确保功能的正确性和可靠性。

#### Acceptance Criteria

1. THE Test_Suite SHALL include unit tests for the invitation creation process
2. THE Test_Suite SHALL include unit tests for the friend search functionality
3. THE Test_Suite SHALL include unit tests for invitation acceptance and rejection
4. THE Test_Suite SHALL include unit tests for abandoning plans in pending status
5. THE Test_Suite SHALL include unit tests for abandoning plans in active status
6. THE Test_Suite SHALL include unit tests for fund freezing and unfreezing operations
7. THE Test_Suite SHALL include unit tests for fund transfer operations
8. THE Test_Suite SHALL include property-based tests for fund operation invariants
9. THE Test_Suite SHALL verify that the sum of all participant balances remains constant after any operation

### Requirement 10: 邀请状态跟踪

**User Story:** 作为计划创建者，我想知道我的邀请是否已被查看和处理，以便我能够跟进。

#### Acceptance Criteria

1. WHEN an invitation is sent, THE Invitation_System SHALL record the invitation timestamp
2. WHEN THE Plan_Participant views the invitation, THE Invitation_System SHALL record the view timestamp
3. WHEN THE Plan_Participant responds to the invitation, THE Invitation_System SHALL record the response timestamp
4. THE Invitation_System SHALL allow THE Plan_Creator to view the invitation status
5. THE Invitation_System SHALL display whether the invitation is pending, viewed, accepted, or rejected

### Requirement 11: 并发邀请处理

**User Story:** 作为系统管理员，我想确保系统能够正确处理同一用户的多个邀请，以便避免冲突和数据不一致。

#### Acceptance Criteria

1. WHEN multiple invitations are sent to the same User, THE Invitation_System SHALL allow THE User to view all pending invitations
2. THE Invitation_System SHALL allow THE User to accept or reject each invitation independently
3. WHEN THE User accepts an invitation, THE Invitation_System SHALL not automatically reject other pending invitations
4. THE Invitation_System SHALL use database locking to prevent race conditions when processing invitation responses
5. IF two users simultaneously try to accept invitations that would exceed their available balance, THEN THE Fund_Manager SHALL process them sequentially and reject the second if insufficient funds exist

### Requirement 12: 邀请验证规则

**User Story:** 作为系统管理员，我想确保邀请遵循业务规则，以便维护系统的完整性。

#### Acceptance Criteria

1. WHEN THE Plan_Creator attempts to send an invitation, THE Invitation_System SHALL verify that THE Plan_Creator has sufficient frozen funds
2. THE Invitation_System SHALL prevent THE Plan_Creator from inviting themselves
3. THE Invitation_System SHALL prevent duplicate invitations for the same plan
4. WHEN THE Plan_Participant attempts to accept an invitation, THE Invitation_System SHALL verify that THE Plan_Participant has sufficient balance to freeze the Stake_Amount
5. IF THE Plan_Participant has insufficient balance, THEN THE Invitation_System SHALL display an error message and prevent acceptance
