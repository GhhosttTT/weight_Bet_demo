# 邀请好友功能实现总结

## 功能概述

已成功实现用户通过邮箱邀请好友参与减肥计划的完整功能，包括后端服务、API 端点和数据库模型。

## 已完成的组件

### 1. 数据库层 ✅
- **invitations 表**: 存储邀请记录，包含状态、时间戳等信息
- **betting_plans 表扩展**: 添加了 abandoned_by, abandoned_at, expiry_checked_at 字段
- **Invitation 模型**: SQLAlchemy 模型，支持状态管理和关系映射
- **数据库索引**: 优化查询性能的索引

### 2. 后端服务层 ✅
- **FriendSearchService**: 通过邮箱搜索好友
  - `search_by_email()`: 搜索用户
  - `validate_email_format()`: 验证邮箱格式
  
- **InvitationService**: 管理邀请生命周期
  - `create_invitation()`: 创建邀请并发送通知
  - `get_invitation_by_plan()`: 根据计划获取邀请
  - `get_user_invitations()`: 获取用户的邀请列表（支持状态筛选）
  - `update_invitation_status()`: 更新邀请状态

- **PlanStatusManager**: 管理计划状态
  - `transition_status()`: 状态转换
  - `check_expired_plans()`: 检查过期计划
  - `abandon_plan()`: 放弃计划

### 3. API 端点 ✅

#### 搜索好友
```
GET /api/users/search?email={email}
```
- 通过邮箱搜索用户
- 返回用户基本信息（姓名、年龄、性别）

#### 发送邀请
```
POST /api/betting-plans/{plan_id}/invite
Body: { "invitee_email": "friend@example.com" }
```
- 邀请好友参与计划
- 验证权限和计划状态
- 自动发送通知

#### 获取邀请列表
```
GET /api/invitations?status={status}
```
- 获取当前用户的邀请列表
- 支持按状态筛选（pending, viewed, accepted, rejected, expired）
- 包含计划基本信息

#### 查看邀请详情
```
GET /api/invitations/{invitation_id}
```
- 获取邀请的完整信息
- 包含完整的计划详情
- 权限验证（只有邀请者和被邀请者可查看）

#### 标记邀请为已查看
```
POST /api/invitations/{invitation_id}/view
```
- 更新 viewed_at 时间戳
- 更新状态为 VIEWED

### 4. 测试覆盖 ✅
- **21 个单元测试**全部通过
- 测试覆盖：
  - 邀请创建（成功和各种错误场景）
  - 邀请查询（按计划、按用户、状态筛选）
  - 状态更新和转换
  - 边界情况和并发场景
  - 权限验证
  - 时间戳顺序验证

## API 使用示例

### 1. 搜索好友
```bash
curl -X GET "http://localhost:8000/api/users/search?email=friend@example.com" \
  -H "Authorization: Bearer {access_token}"
```

响应：
```json
{
  "user_id": "uuid",
  "nickname": "张三",
  "age": 25,
  "gender": "male"
}
```

### 2. 发送邀请
```bash
curl -X POST "http://localhost:8000/api/betting-plans/{plan_id}/invite" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"invitee_email": "friend@example.com"}'
```

响应：
```json
{
  "invitation_id": "uuid",
  "plan_id": "uuid",
  "inviter_id": "uuid",
  "invitee_email": "friend@example.com",
  "invitee_id": "uuid",
  "status": "pending",
  "sent_at": "2024-01-01T00:00:00Z"
}
```

### 3. 获取邀请列表
```bash
curl -X GET "http://localhost:8000/api/invitations?status=pending" \
  -H "Authorization: Bearer {access_token}"
```

响应：
```json
{
  "invitations": [
    {
      "invitation_id": "uuid",
      "plan_id": "uuid",
      "inviter_id": "uuid",
      "inviter_name": "李四",
      "invitee_email": "me@example.com",
      "status": "pending",
      "sent_at": "2024-01-01T00:00:00Z",
      "bet_amount": 100.0,
      "target_weight_loss": 5.0,
      "duration_days": 30,
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  ],
  "total": 1
}
```

### 4. 查看邀请详情
```bash
curl -X GET "http://localhost:8000/api/invitations/{invitation_id}" \
  -H "Authorization: Bearer {access_token}"
```

响应：
```json
{
  "invitation_id": "uuid",
  "status": "pending",
  "sent_at": "2024-01-01T00:00:00Z",
  "plan": {
    "plan_id": "uuid",
    "creator_id": "uuid",
    "creator_name": "李四",
    "bet_amount": 100.0,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "creator_initial_weight": 80.0,
    "creator_target_weight": 75.0,
    "creator_target_weight_loss": 5.0,
    "description": "一起减肥吧！",
    "status": "pending"
  }
}
```

### 5. 标记为已查看
```bash
curl -X POST "http://localhost:8000/api/invitations/{invitation_id}/view" \
  -H "Authorization: Bearer {access_token}"
```

响应：
```json
{
  "invitation_id": "uuid",
  "status": "viewed",
  "viewed_at": "2024-01-01T00:00:00Z",
  "message": "邀请已标记为已查看"
}
```

## 邀请状态流转

```
PENDING (待处理)
   ↓
VIEWED (已查看)
   ↓
ACCEPTED (已接受) / REJECTED (已拒绝) / EXPIRED (已过期)
```

## 安全特性

1. **权限验证**: 所有端点都需要 JWT 认证
2. **邮箱验证**: 自动验证邮箱格式
3. **重复检查**: 防止重复邀请同一计划
4. **自我邀请防护**: 不能邀请自己
5. **状态验证**: 只能邀请 PENDING 状态的计划
6. **权限控制**: 只有创建者可以发送邀请

## 通知集成

邀请创建时会自动发送通知给被邀请者，包含：
- 邀请者姓名
- 赌金金额
- 目标减重
- 计划时长
- 开始和结束日期

## 下一步

邀请功能的后端核心已完成，可以开始：
1. 实现前端 UI（Android）
2. 实现接受/拒绝邀请的逻辑
3. 添加更多通知类型（接受、拒绝等）
4. 实现邀请过期清理定时任务

## 技术栈

- **后端框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **认证**: JWT
- **测试**: pytest + Hypothesis
- **通知**: Firebase Cloud Messaging (FCM)
