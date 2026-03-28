# 实现计划: 邀请好友和放弃计划功能

## 概述

本实现计划将邀请好友和放弃计划功能分解为可执行的编码任务。实现采用 Python FastAPI 后端和 Kotlin Android 前端架构，确保资金操作的原子性和数据一致性。

## 任务列表

- [x] 1. 数据库迁移和模型定义
  - [x] 1.1 创建 invitations 表迁移脚本
    - 使用 Alembic 创建迁移文件
    - 定义表结构（id, plan_id, inviter_id, invitee_email, invitee_id, status, sent_at, viewed_at, responded_at）
    - 添加外键约束和索引
    - 添加状态检查约束
    - _需求: 1.1, 1.2, 10.1, 10.2, 10.3_
  
  - [x] 1.2 扩展 betting_plans 表
    - 添加 abandoned_by, abandoned_at, expiry_checked_at 字段
    - 添加 expired 状态到 plan_status 枚举
    - 添加外键约束
    - _需求: 3.1, 3.6, 6.2_
  
  - [x] 1.3 创建 Invitation SQLAlchemy 模型
    - 定义 Invitation 类和 InvitationStatus 枚举
    - 配置关系映射（plan, inviter, invitee）
    - 添加验证规则
    - _需求: 1.1, 10.1, 10.2, 10.3_
  
  - [x] 1.4 添加数据库索引优化
    - 创建 idx_invitations_invitee_email 索引
    - 创建 idx_betting_plans_end_date_status 索引
    - 创建 idx_invitations_invitee_status 索引
    - _需求: 4.4, 11.4_

- [ ] 2. 后端服务层实现
  - [x] 2.1 实现 FriendSearchService
    - 实现 search_by_email 方法
    - 实现 validate_email_format 方法
    - 返回 UserSearchResult（只包含公开信息）
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.2 为 FriendSearchService 编写单元测试
    - 测试有效邮箱搜索
    - 测试无效邮箱格式
    - 测试用户不存在情况
    - _需求: 9.2_
  
  - [x] 2.3 实现 InvitationService.create_invitation
    - 验证计划状态和权限
    - 验证邮箱格式和用户存在性
    - 检查重复邀请
    - 创建邀请记录
    - 触发通知发送
    - _需求: 1.2, 1.3, 1.4, 1.5, 12.1, 12.2, 12.3_
  
  - [x] 2.4 实现 InvitationService 查询方法
    - 实现 get_invitation_by_plan
    - 实现 get_user_invitations（支持状态筛选）
    - 实现 update_invitation_status
    - _需求: 1.7, 10.4, 10.5, 11.1_
  
  - [x] 2.5 为 InvitationService 编写单元测试
    - 测试邀请创建成功场景
    - 测试重复邀请拒绝
    - 测试邀请自己拒绝
    - 测试状态更新
    - _需求: 9.1, 9.3_

- [ ] 3. 计划状态管理实现
  - [x] 3.1 实现 PlanStatusManager.transition_status
    - 验证状态转换合法性
    - 执行状态转换逻辑
    - 记录状态变更时间戳
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.7_
  
  - [x] 3.2 实现 PlanStatusManager.abandon_plan
    - 验证用户权限
    - 根据计划状态调用相应的放弃逻辑
    - 返回 AbandonResult
    - _需求: 5.1, 5.3, 6.1, 6.5_
  
  - [x] 3.3 实现 PlanStatusManager.check_expired_plans
    - 查询所有 active 状态且已过期的计划
    - 标记为 expired 状态
    - 发送过期通知
    - _需求: 3.6, 4.1, 4.2, 4.3_
  
  - [x] 3.4 为 PlanStatusManager 编写单元测试
    - 测试各种状态转换
    - 测试过期检查逻辑
    - 测试权限验证
    - _需求: 9.4, 9.5_

- [x] 4. 资金管理实现
  - [x] 4.1 实现 FundManager.freeze_funds
    - 验证余额充足性
    - 执行原子性冻结操作
    - 创建交易记录
    - _需求: 7.1, 7.2, 7.3, 12.4_
  
  - [x] 4.2 实现 FundManager.unfreeze_funds
    - 执行原子性解冻操作
    - 创建交易记录
    - _需求: 5.2, 5.4, 7.1, 7.2, 7.3_
  
  - [x] 4.3 实现 FundManager.transfer_funds
    - 执行原子性转账操作
    - 创建交易记录
    - _需求: 6.3, 6.4, 7.1, 7.2, 7.3_
  
  - [x] 4.4 实现 FundManager.process_abandon_refund
    - 根据计划状态处理退款逻辑
    - pending 状态：解冻创建者资金
    - active 状态：转账给获胜方
    - 使用数据库事务确保原子性
    - _需求: 5.2, 6.3, 6.4, 7.1, 7.2, 7.4_
  
  - [x] 4.5 为 FundManager 编写单元测试
    - 测试冻结操作
    - 测试解冻操作
    - 测试转账操作
    - 测试余额不足情况
    - _需求: 9.6, 9.7_
  
  - [x] 4.6 为资金操作编写属性测试
    - **Property 19: 总余额守恒**
    - **验证需求: 7.4, 9.9**
    - 使用 Hypothesis 生成随机金额和余额
    - 验证任何资金操作前后总余额相等

- [ ] 5. 放弃计划核心逻辑
  - [ ] 5.1 实现 abandon_pending_plan 函数
    - 验证计划状态为 PENDING
    - 验证用户为创建者
    - 使用数据库事务
    - 解冻创建者资金
    - 更新计划状态为 CANCELLED
    - 更新邀请状态为 EXPIRED
    - 发送通知
    - _需求: 5.1, 5.2, 5.3, 5.6_
  
  - [ ] 5.2 实现 abandon_active_plan 函数
    - 验证计划状态为 ACTIVE
    - 验证用户为参与者之一
    - 使用数据库事务和行锁
    - 确定获胜方和失败方
    - 解冻双方资金
    - 转账给获胜方
    - 更新计划状态和 abandoned_by 字段
    - 发送通知
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [ ] 5.3 为放弃计划逻辑编写单元测试
    - 测试放弃 pending 计划
    - 测试放弃 active 计划
    - 测试权限验证
    - 测试资金正确处理
    - _需求: 9.4, 9.5_

- [ ] 6. API 端点实现
  - [x] 6.1 实现 GET /api/users/search 端点
    - 接收 email 查询参数
    - 调用 FriendSearchService
    - 返回用户基本信息或 404
    - 处理邮箱格式错误（400）
    - _需求: 1.3, 2.1, 2.2, 2.5_
  
  - [x] 6.2 实现 POST /api/betting-plans/{plan_id}/invite 端点
    - 接收 invitee_email
    - 验证用户认证和权限
    - 调用 InvitationService.create_invitation
    - 返回邀请对象或错误
    - _需求: 1.2, 1.5, 1.6_
  
  - [x] 6.3 实现 GET /api/invitations 端点
    - 支持 status 查询参数筛选
    - 返回当前用户的邀请列表
    - _需求: 10.4, 11.1_
  
  - [x] 6.4 实现 GET /api/invitations/{invitation_id} 端点
    - 返回邀请详情和完整计划信息
    - 验证用户权限
    - _需求: 1.7, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 6.5 实现 POST /api/invitations/{invitation_id}/view 端点
    - 更新 viewed_at 时间戳
    - 更新状态为 VIEWED
    - _需求: 10.2_
  
  - [ ] 6.6 实现 POST /api/betting-plans/{plan_id}/abandon 端点
    - 接收 confirmation 参数
    - 验证用户认证和权限
    - 调用 PlanStatusManager.abandon_plan
    - 返回 AbandonResult
    - _需求: 5.1, 6.1, 6.7_
  
  - [ ] 6.7 为 API 端点编写集成测试
    - 测试完整邀请流程（搜索 → 邀请 → 接受）
    - 测试放弃 pending 计划流程
    - 测试放弃 active 计划流程
    - 测试错误处理和边界情况

- [ ] 7. 通知服务集成
  - [ ] 7.1 实现邀请通知发送
    - 创建 INVITATION_RECEIVED 通知类型
    - 包含所有必需信息（邀请者姓名、赌金、目标、时长）
    - 调用推送通知服务
    - 保存通知历史
    - _需求: 1.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ] 7.2 实现邀请响应通知
    - 创建 INVITATION_ACCEPTED 通知类型
    - 创建 INVITATION_REJECTED 通知类型
    - 发送给计划创建者
    - _需求: 5.6_
  
  - [ ] 7.3 实现计划放弃通知
    - 创建 PLAN_ABANDONED 通知类型
    - 包含获胜金额信息
    - 发送给获胜方
    - _需求: 6.6_
  
  - [ ] 7.4 实现计划过期通知
    - 创建 PLAN_EXPIRED 通知类型
    - 发送给双方参与者
    - _需求: 4.3_

- [ ] 8. 定时任务实现
  - [ ] 8.1 创建 Celery 任务配置
    - 配置 Celery app
    - 配置 Redis broker
    - 配置 beat schedule
  
  - [ ] 8.2 实现 check_expired_plans 定时任务
    - 每小时执行一次
    - 调用 PlanStatusManager.check_expired_plans
    - 记录执行日志
    - _需求: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 8.3 实现 cleanup_expired_invitations 定时任务
    - 每天执行一次
    - 清理超过 7 天未响应的邀请
    - 标记为 EXPIRED 状态

- [ ] 9. Android 前端 - 数据层
  - [ ] 9.1 定义 Kotlin 数据模型
    - 创建 Invitation 数据类
    - 创建 UserSearchResult 数据类
    - 创建 InviteFriendRequest 数据类
    - 创建 AbandonPlanRequest 数据类
    - 创建 AbandonPlanResult 数据类
    - 添加 JSON 序列化注解
    - _需求: 1.1, 2.4, 5.1, 6.1_
  
  - [ ] 9.2 扩展 ApiService 接口
    - 添加 searchFriend 方法
    - 添加 inviteFriend 方法
    - 添加 getInvitations 方法
    - 添加 getInvitationDetails 方法
    - 添加 markInvitationViewed 方法
    - 添加 abandonPlan 方法
    - _需求: 1.3, 1.5, 1.7, 10.2, 10.4_
  
  - [ ] 9.3 实现 InvitationRepository
    - 实现搜索好友方法
    - 实现发送邀请方法
    - 实现获取邀请列表方法
    - 实现标记已查看方法
    - 处理网络错误和缓存
    - _需求: 1.3, 1.5, 10.2, 10.4, 11.1_
  
  - [ ] 9.4 扩展 BettingPlanRepository
    - 添加 abandonPlan 方法
    - 处理放弃计划的网络请求
    - 更新本地缓存
    - _需求: 5.1, 6.1_

- [ ] 10. Android 前端 - UI 组件
  - [ ] 10.1 创建 InviteFriendDialog
    - 创建布局文件（邮箱输入、搜索按钮、结果显示）
    - 实现邮箱格式验证
    - 实现搜索逻辑
    - 显示搜索结果（姓名、年龄）
    - 实现确认邀请按钮
    - 处理错误提示
    - _需求: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.5_
  
  - [ ] 10.2 创建 InvitationListFragment
    - 创建布局文件（RecyclerView）
    - 创建邀请项 CardView 布局
    - 实现邀请列表适配器
    - 显示邀请信息（邀请者、赌金、时长、目标）
    - 实现查看详情、接受、拒绝按钮
    - 根据状态显示不同 UI
    - _需求: 1.7, 1.8, 10.4, 10.5, 11.1_
  
  - [ ] 10.3 创建 AbandonPlanDialog
    - 创建确认对话框布局
    - 根据计划状态显示不同警告信息
    - pending: "将退还赌金"
    - active: "将失去赌金，对方获胜"
    - 添加确认复选框
    - 实现确认按钮（初始禁用）
    - 使用危险样式（红色）
    - _需求: 5.1, 6.1, 6.7_
  
  - [ ] 10.4 扩展 PlanDetailFragment
    - 添加"放弃计划"按钮
    - 根据计划状态控制按钮可见性
    - pending: 创建者可见
    - active: 双方可见
    - 其他状态: 不可见
    - 点击按钮显示 AbandonPlanDialog
    - _需求: 5.1, 6.1_

- [ ] 11. Android 前端 - ViewModel
  - [ ] 11.1 创建 InviteFriendViewModel
    - 实现搜索好友逻辑
    - 实现发送邀请逻辑
    - 管理 UI 状态（loading, success, error）
    - 处理邮箱验证
    - _需求: 1.2, 1.3, 1.5, 2.1_
  
  - [ ] 11.2 创建 InvitationListViewModel
    - 实现获取邀请列表逻辑
    - 实现状态筛选
    - 实现标记已查看逻辑
    - 实现接受/拒绝邀请逻辑
    - 管理列表状态
    - _需求: 1.7, 1.8, 10.2, 10.4, 11.1, 11.2, 11.3_
  
  - [ ] 11.3 扩展 PlanDetailViewModel
    - 添加放弃计划逻辑
    - 处理确认流程
    - 更新计划状态
    - 处理成功/失败回调
    - _需求: 5.1, 5.3, 6.1, 6.5_

- [ ] 12. 并发控制和数据一致性
  - [ ] 12.1 实现邀请接受的并发控制
    - 使用数据库行锁（SELECT FOR UPDATE）
    - 验证余额充足性
    - 处理并发接受场景
    - _需求: 11.4, 11.5, 12.4, 12.5_
  
  - [ ] 12.2 实现资金操作的事务管理
    - 确保所有资金操作在事务中执行
    - 实现回滚机制
    - 记录审计日志
    - _需求: 7.1, 7.2, 7.5_
  
  - [ ] 12.3 编写并发场景测试
    - 测试同时接受多个邀请
    - 测试余额不足场景
    - 测试并发放弃计划
    - _需求: 11.4, 11.5_

- [ ] 13. 集成和端到端测试
  - [ ] 13.1 编写完整邀请流程测试
    - 创建计划 → 搜索好友 → 发送邀请 → 接受邀请
    - 验证状态转换
    - 验证资金冻结
    - 验证通知发送
    - _需求: 1.1-1.8, 3.3_
  
  - [ ] 13.2 编写放弃 pending 计划流程测试
    - 创建计划 → 发送邀请 → 放弃计划
    - 验证状态变为 CANCELLED
    - 验证资金解冻
    - 验证通知发送
    - _需求: 5.1-5.6_
  
  - [ ] 13.3 编写放弃 active 计划流程测试
    - 创建计划 → 接受邀请 → 放弃计划
    - 验证状态变为 CANCELLED
    - 验证资金转账
    - 验证获胜方收到通知
    - _需求: 6.1-6.7_
  
  - [ ] 13.4 编写拒绝邀请流程测试
    - 创建计划 → 发送邀请 → 拒绝邀请
    - 验证状态变为 REJECTED
    - 验证创建者资金解冻
    - 验证通知发送
    - _需求: 3.4, 5.4, 5.5_

- [ ] 14. 检查点 - 后端核心功能验证
  - 确保所有后端单元测试通过
  - 确保资金操作的原子性
  - 确保状态转换正确
  - 如有问题请询问用户

- [ ] 15. 检查点 - 前端功能验证
  - 确保所有 UI 组件正常显示
  - 确保网络请求正确处理
  - 确保错误提示友好
  - 如有问题请询问用户

- [ ] 16. 部署准备
  - [ ] 16.1 运行数据库迁移
    - 在测试环境执行 alembic upgrade head
    - 验证表结构和索引
    - 验证数据完整性约束
  
  - [ ] 16.2 配置定时任务
    - 启动 Celery worker
    - 启动 Celery beat
    - 验证定时任务执行
    - 监控任务日志
  
  - [ ] 16.3 配置通知服务
    - 设置 FCM_SERVER_KEY 环境变量
    - 验证推送通知功能
    - 测试通知发送
  
  - [ ] 16.4 性能测试和监控
    - 测试 API 响应时间
    - 测试并发处理能力
    - 配置日志和监控
    - 设置告警规则

- [ ] 17. 最终检查点
  - 确保所有测试通过（单元测试、集成测试、属性测试）
  - 确保代码覆盖率达标（> 85%）
  - 确保所有需求都已实现
  - 确保文档更新完整
  - 如有问题请询问用户

## 注意事项

- 标记 `*` 的任务为可选测试任务，可根据时间安排跳过
- 每个任务都明确引用了相关需求编号，确保可追溯性
- 资金操作必须使用数据库事务，确保原子性
- 并发场景必须使用数据库锁，防止竞态条件
- 所有 API 端点必须进行权限验证
- 通知发送失败不应影响核心业务逻辑
