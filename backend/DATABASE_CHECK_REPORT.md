# 数据库表检查报告

## 检查时间
2026-03-23 17:15:00

## 检查结果
✅ **所有必需的表都已创建 (11/11)**

## 数据库信息
- **数据库类型**: SQLite
- **数据库文件**: weight_loss_betting.db
- **表总数**: 11
- **当前用户数**: 2

## 已创建的表

### 1. users (用户表)
**列数**: 12
**主键**: id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 用户ID
- email (VARCHAR(255), NOT NULL) - 邮箱
- password_hash (VARCHAR(255), NOT NULL) - 密码哈希
- nickname (VARCHAR(50), NOT NULL) - 昵称
- gender (VARCHAR(6), NOT NULL) - 性别
- age (INTEGER, NOT NULL) - 年龄
- height (FLOAT, NOT NULL) - 身高
- current_weight (FLOAT, NOT NULL) - 当前体重
- target_weight (FLOAT, NULL) - 目标体重
- payment_method_id (VARCHAR(255), NULL) - 支付方式ID
- created_at (DATETIME, NOT NULL) - 创建时间
- updated_at (DATETIME, NOT NULL) - 更新时间

### 2. balances (余额表)
**列数**: 4
**主键**: user_id
**外键**: user_id -> users.id
**列信息**:
- user_id (VARCHAR(36), NOT NULL) - 用户ID
- available_balance (FLOAT, NOT NULL) - 可用余额
- frozen_balance (FLOAT, NOT NULL) - 冻结余额
- updated_at (DATETIME, NOT NULL) - 更新时间

### 3. betting_plans (对赌计划表)
**列数**: 16
**主键**: id
**外键**: 
- creator_id -> users.id
- participant_id -> users.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 计划ID
- creator_id (VARCHAR(36), NOT NULL) - 创建者ID
- participant_id (VARCHAR(36), NULL) - 参与者ID
- status (VARCHAR(9), NOT NULL) - 状态
- bet_amount (FLOAT, NOT NULL) - 对赌金额
- start_date (DATETIME, NOT NULL) - 开始日期
- end_date (DATETIME, NOT NULL) - 结束日期
- description (TEXT, NULL) - 描述
- creator_initial_weight (FLOAT, NOT NULL) - 创建者初始体重
- creator_target_weight (FLOAT, NOT NULL) - 创建者目标体重
- creator_target_weight_loss (FLOAT, NOT NULL) - 创建者目标减重
- participant_initial_weight (FLOAT, NULL) - 参与者初始体重
- participant_target_weight (FLOAT, NULL) - 参与者目标体重
- participant_target_weight_loss (FLOAT, NULL) - 参与者目标减重
- created_at (DATETIME, NOT NULL) - 创建时间
- activated_at (DATETIME, NULL) - 激活时间

### 4. check_ins (打卡记录表)
**列数**: 11
**主键**: id
**外键**: 
- user_id -> users.id
- plan_id -> betting_plans.id
- reviewer_id -> users.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 打卡ID
- user_id (VARCHAR(36), NOT NULL) - 用户ID
- plan_id (VARCHAR(36), NOT NULL) - 计划ID
- weight (FLOAT, NOT NULL) - 体重
- check_in_date (DATE, NOT NULL) - 打卡日期
- photo_url (VARCHAR(500), NULL) - 照片URL
- note (TEXT, NULL) - 备注
- review_status (VARCHAR(8), NOT NULL) - 审核状态
- reviewer_id (VARCHAR(36), NULL) - 审核者ID
- review_comment (TEXT, NULL) - 审核评论
- created_at (DATETIME, NOT NULL) - 创建时间

### 5. settlements (结算记录表)
**列数**: 13
**主键**: id
**外键**: plan_id -> betting_plans.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 结算ID
- plan_id (VARCHAR(36), NOT NULL) - 计划ID
- creator_achieved (BOOLEAN, NOT NULL) - 创建者是否达成
- participant_achieved (BOOLEAN, NOT NULL) - 参与者是否达成
- creator_final_weight (FLOAT, NOT NULL) - 创建者最终体重
- participant_final_weight (FLOAT, NOT NULL) - 参与者最终体重
- creator_weight_loss (FLOAT, NOT NULL) - 创建者减重量
- participant_weight_loss (FLOAT, NOT NULL) - 参与者减重量
- creator_amount (FLOAT, NOT NULL) - 创建者金额
- participant_amount (FLOAT, NOT NULL) - 参与者金额
- platform_fee (FLOAT, NOT NULL) - 平台费用
- notes (TEXT, NULL) - 备注
- settlement_date (DATETIME, NOT NULL) - 结算日期

### 6. transactions (交易记录表)
**列数**: 9
**主键**: id
**外键**: 
- user_id -> users.id
- related_plan_id -> betting_plans.id
- related_settlement_id -> settlements.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 交易ID
- user_id (VARCHAR(36), NOT NULL) - 用户ID
- type (VARCHAR(8), NOT NULL) - 交易类型
- amount (FLOAT, NOT NULL) - 金额
- status (VARCHAR(9), NOT NULL) - 状态
- related_plan_id (VARCHAR(36), NULL) - 关联计划ID
- related_settlement_id (VARCHAR(36), NULL) - 关联结算ID
- created_at (DATETIME, NOT NULL) - 创建时间
- completed_at (DATETIME, NULL) - 完成时间

### 7. audit_logs (审计日志表)
**列数**: 9
**主键**: id
**外键**: user_id -> users.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 日志ID
- user_id (VARCHAR(36), NULL) - 用户ID
- action (VARCHAR(100), NOT NULL) - 操作
- resource_type (VARCHAR(50), NOT NULL) - 资源类型
- resource_id (VARCHAR(36), NULL) - 资源ID
- details (JSON, NULL) - 详情
- ip_address (VARCHAR(45), NULL) - IP地址
- user_agent (TEXT, NULL) - 用户代理
- created_at (DATETIME, NOT NULL) - 创建时间

### 8. user_badges (用户徽章表)
**列数**: 4
**主键**: id
**外键**: user_id -> users.id
**列信息**:
- id (VARCHAR, NOT NULL) - 徽章ID
- user_id (VARCHAR, NOT NULL) - 用户ID
- badge_type (VARCHAR(18), NOT NULL) - 徽章类型
- earned_at (DATETIME, NULL) - 获得时间

### 9. comments (评论表)
**列数**: 5
**主键**: id
**外键**: 
- plan_id -> betting_plans.id
- user_id -> users.id
**列信息**:
- id (VARCHAR, NOT NULL) - 评论ID
- plan_id (VARCHAR, NOT NULL) - 计划ID
- user_id (VARCHAR, NOT NULL) - 用户ID
- content (TEXT, NOT NULL) - 内容
- created_at (DATETIME, NULL) - 创建时间

### 10. device_tokens (设备令牌表)
**列数**: 6
**主键**: id
**外键**: user_id -> users.id
**列信息**:
- id (VARCHAR, NOT NULL) - 令牌ID
- user_id (VARCHAR, NOT NULL) - 用户ID
- token (VARCHAR, NOT NULL) - 令牌
- platform (VARCHAR(7), NOT NULL) - 平台
- created_at (DATETIME, NULL) - 创建时间
- updated_at (DATETIME, NULL) - 更新时间

### 11. disputes (争议记录表)
**列数**: 11
**主键**: id
**外键**: 
- settlement_id -> settlements.id
- user_id -> users.id
**列信息**:
- id (VARCHAR(36), NOT NULL) - 争议ID
- settlement_id (VARCHAR(36), NOT NULL) - 结算ID
- user_id (VARCHAR(36), NOT NULL) - 用户ID
- reason (TEXT, NOT NULL) - 原因
- description (TEXT, NULL) - 描述
- status (VARCHAR(12), NOT NULL) - 状态
- admin_notes (TEXT, NULL) - 管理员备注
- resolved_by (VARCHAR(36), NULL) - 解决者
- resolved_at (DATETIME, NULL) - 解决时间
- created_at (DATETIME, NOT NULL) - 创建时间
- updated_at (DATETIME, NOT NULL) - 更新时间

## 数据库关系图

```
users (用户)
  ├─> balances (余额)
  ├─> betting_plans (对赌计划) [作为创建者]
  ├─> betting_plans (对赌计划) [作为参与者]
  ├─> check_ins (打卡记录)
  ├─> transactions (交易记录)
  ├─> audit_logs (审计日志)
  ├─> user_badges (用户徽章)
  ├─> comments (评论)
  ├─> device_tokens (设备令牌)
  └─> disputes (争议记录)

betting_plans (对赌计划)
  ├─> check_ins (打卡记录)
  ├─> settlements (结算记录)
  ├─> transactions (交易记录)
  └─> comments (评论)

settlements (结算记录)
  ├─> transactions (交易记录)
  └─> disputes (争议记录)
```

## 数据完整性检查

✅ **所有外键关系正确建立**
✅ **所有主键约束正确设置**
✅ **数据类型定义合理**
✅ **必填字段和可选字段设置正确**

## 测试结果

### 基本操作测试
✅ 数据库连接成功
✅ 表查询操作正常
✅ 当前已有 2 个测试用户

### 示例数据
- 用户1: test@example.com
- 用户2: testuser@example.com

## 结论

🎉 **数据库结构完整，所有必需的表都已正确创建，可以正常使用！**

## 建议

1. ✅ 数据库表结构完整，无需额外操作
2. ✅ 可以开始使用所有 API 功能
3. ⚠️ 建议定期备份数据库文件
4. ⚠️ 生产环境建议迁移到 PostgreSQL

---

**检查脚本**: `backend/check_database.py`
**最后更新**: 2026-03-23 17:15:00
