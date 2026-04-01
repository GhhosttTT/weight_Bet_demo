# 合并实现计划

## 概述

本实现计划合并了减肥对赌 APP 的所有任务，包括：
- 核心应用实现计划
- 好友邀请和计划放弃功能实现计划
- 充值后余额未更新 Bug 修复计划
- 健身推荐系统实现计划

---

## 第一部分：核心应用实现任务

### 第一阶段: 后端 API 和核心服务

- [x] 1. 搭建后端项目基础架构
  - 创建 FastAPI 项目结构
  - 配置数据库连接
  - 配置 Redis 缓存连接
  - 设置环境变量管理
  - 配置日志系统
  - 设置 CORS 和安全中间件

- [x] 2. 实现数据模型和数据库迁移
  - [x] 2.1 创建用户数据模型 (User)
  - [x] 2.2 创建对赌计划数据模型 (BettingPlan)
  - [x] 2.3 创建打卡记录数据模型 (CheckIn)
  - [x] 2.4 创建结算记录数据模型 (Settlement)
  - [x] 2.5 创建交易记录数据模型 (Transaction)
  - [x] 2.6 创建账户余额数据模型 (Balance)

- [x] 3. 实现认证服务 (AuthService)
  - [x] 3.1 实现用户注册功能
  - [x] 3.2 实现用户登录功能
  - [x] 3.3 实现第三方登录 (Google OAuth)
  - [x] 3.4 实现令牌刷新功能
  - [x] 3.5 实现 JWT 令牌验证中间件

- [x] 4. 实现用户服务 (UserService)
  - [x] 4.1 实现获取用户信息功能
  - [x] 4.2 实现更新用户信息功能
  - [x] 4.3 实现绑定支付方式功能

- [x] 5. 实现支付服务 (PaymentService)
  - [x] 5.1 实现资金冻结功能
  - [x] 5.2 实现资金解冻功能
  - [x] 5.3 实现资金转账功能
  - [x] 5.4 实现获取账户余额功能
  - [x] 5.5 实现交易历史查询功能
  - [x] 5.6 集成第三方支付网关
  - [x] 5.7 实现提现功能

- [x] 6. 实现对赌计划服务 (BettingPlanService)
  - [x] 6.1 实现创建对赌计划功能
  - [x] 6.2 实现邀请参与者功能
  - [x] 6.3 实现接受对赌计划功能
  - [x] 6.4 实现拒绝和取消计划功能
  - [x] 6.5 实现获取计划详情功能
  - [x] 6.6 实现获取用户计划列表功能

- [x] 7. 实现打卡服务 (CheckInService)
  - [x] 7.1 实现创建打卡记录功能
  - [x] 7.2 实现上传体重秤照片功能
  - [x] 7.3 实现审核打卡记录功能
  - [x] 7.4 实现获取打卡历史功能
  - [x] 7.5 实现计算进度统计功能

- [x] 8. 实现结算服务 (SettlementService)
  - 实现结算计算逻辑
  - 实现执行结算功能
  - 实现定时结算任务
  - 实现获取结算详情功能

- [x] 9. 实现通知服务 (NotificationService)
  - 集成 Firebase Cloud Messaging
  - 实现通知发送功能
  - 实现打卡提醒定时任务

- [x] 10. 实现社交服务 (SocialService)
  - 实现排行榜功能
  - 实现评论功能
  - 实现鼓励功能
  - 实现勋章系统
  - 实现群组挑战功能

### 第二阶段: Android 客户端实现

- [x] 17. 搭建 Android 项目基础架构
  - 创建 Android 项目 (Kotlin)
  - 配置 Gradle 依赖
  - 设置项目结构 (MVVM 架构)
  - 配置 Retrofit 网络库
  - 配置 Room 本地数据库
  - 配置 Hilt 依赖注入

- [x] 18. 实现 Android 网络层
  - [x] 18.1 创建 API 接口定义
  - [x] 18.2 实现网络请求管理

- [x] 19. 实现 Android 本地存储
  - [x] 19.1 创建 Room 数据库
  - [x] 19.2 实现本地缓存策略
  - [x] 19.3 实现离线队列

---

## 第二部分：好友邀请和计划放弃任务

- [x] 1. 数据库迁移和模型定义
  - [x] 1.1 创建 invitations 表迁移脚本
  - [x] 1.2 扩展 betting_plans 表
  - [x] 1.3 创建 Invitation SQLAlchemy 模型
  - [x] 1.4 添加数据库索引优化

- [ ] 2. 后端服务层实现
  - [x] 2.1 实现 FriendSearchService
  - [x] 2.3 实现 InvitationService.create_invitation
  - [x] 2.4 实现 InvitationService 查询方法

- [ ] 3. 计划状态管理实现
  - [x] 3.1 实现 PlanStatusManager.transition_status
  - [x] 3.2 实现 PlanStatusManager.abandon_plan
  - [x] 3.3 实现 PlanStatusManager.check_expired_plans

- [x] 4. 资金管理实现
  - [x] 4.1 实现 FundManager.freeze_funds
  - [x] 4.2 实现 FundManager.unfreeze_funds
  - [x] 4.3 实现 FundManager.transfer_funds
  - [x] 4.4 实现 FundManager.process_abandon_refund

- [ ] 5. 放弃计划核心逻辑
  - [ ] 5.1 实现 abandon_pending_plan 函数
  - [ ] 5.2 实现 abandon_active_plan 函数
  - [ ] 5.3 为放弃计划逻辑编写单元测试

- [ ] 6. API 端点实现
  - [x] 6.1 实现 GET /api/users/search 端点
  - [x] 6.2 实现 POST /api/betting-plans/{plan_id}/invite 端点
  - [x] 6.3 实现 GET /api/invitations 端点
  - [x] 6.4 实现 GET /api/invitations/{invitation_id} 端点
  - [x] 6.5 实现 POST /api/invitations/{invitation_id}/view 端点
  - [ ] 6.6 实现 POST /api/betting-plans/{plan_id}/abandon 端点

- [ ] 7. 通知服务集成
  - [ ] 7.1 实现邀请通知发送
  - [ ] 7.2 实现邀请响应通知
  - [ ] 7.3 实现计划放弃通知
  - [ ] 7.4 实现计划过期通知

- [ ] 8. 定时任务实现
  - [ ] 8.1 创建 Celery 任务配置
  - [ ] 8.2 实现 check_expired_plans 定时任务
  - [ ] 8.3 实现 cleanup_expired_invitations 定时任务

- [ ] 9. Android 前端 - 数据层
  - [ ] 9.1 定义 Kotlin 数据模型
  - [ ] 9.2 扩展 ApiService 接口
  - [ ] 9.3 实现 InvitationRepository
  - [ ] 9.4 扩展 BettingPlanRepository

- [ ] 10. Android 前端 - UI 组件
  - [ ] 10.1 创建 InviteFriendDialog
  - [ ] 10.2 创建 InvitationListFragment
  - [ ] 10.3 创建 AbandonPlanDialog
  - [ ] 10.4 扩展 PlanDetailFragment

- [ ] 11. Android 前端 - ViewModel
  - [ ] 11.1 创建 InviteFriendViewModel
  - [ ] 11.2 创建 InvitationListViewModel
  - [ ] 11.3 扩展 PlanDetailViewModel

---

## 第三部分：充值后余额未更新 Bug 修复任务

- [x] 1. 编写 bug condition 探索测试
  - 测试充值成功后余额未更新
  - 在未修复代码上运行测试
  - 验证 bug 存在

- [x] 2. 编写保留属性测试
  - 观察非 bug 场景的行为
  - 编写基于属性的测试
  - 在未修复代码上运行测试

- [x] 3. 修复充值后余额未更新
  - [x] 3.1 实现后端 charge 端点修复
    - 定位后端 charge 端点处理函数
    - 添加余额更新逻辑
    - 确保事务完整性
    - 创建交易记录
    - 返回更新后的余额
    - 添加日志记录
  - [ ] 3.2 验证 bug condition 探索测试现在通过
  - [ ] 3.3 验证保留测试仍然通过

- [x] 4. 检查点 - 确保所有测试通过

---

## 第四部分：健身推荐系统实现任务

### 后端任务

- [x] 1. 修改推荐服务，正确处理日期序列化
  - 使用 `model_dump_json()` 代替 `model_dump()`
  - 修复 Redis 缓存的日期序列化问题
  - 为 `FakeRedis` 添加 `setex` 方法

### Android 任务

- [x] 1. 创建推荐缓存管理器
  - 创建 `RecommendationCacheManager.kt`
  - 实现缓存到 SharedPreferences
  - 实现获取缓存推荐方法
  - 实现清空缓存方法

- [x] 2. 修改推荐仓库
  - 集成推荐缓存管理器
  - `getRecommendation()` 优先从缓存读取
  - 添加 `cacheRecommendation()` 方法
  - 添加 `getCachedRecommendation()` 方法

- [x] 3. 修改管家页面
  - 修改 `CoachViewModel` 只读取缓存
  - 修改 `CoachFragment` 添加空状态处理
  - 修改布局添加空状态提示

- [x] 4. 修改登录和打卡流程
  - 修改 `LoginViewModel` 登录成功后异步获取推荐
  - 修改 `CheckInViewModel` 打卡成功后异步刷新推荐
  - 推荐获取失败不影响主流程

- [x] 5. 配置依赖注入
  - 在 `RecommendationCacheManager` 中使用 `@ApplicationContext`
  - 在 `RepositoryModule` 中添加 `RecommendationRepository` 提供方法

---

## 注意事项

- 标记 `*` 的任务为可选测试任务，可根据时间安排跳过
- 每个任务都明确引用了相关需求编号，确保可追溯性
- 资金操作必须使用数据库事务，确保原子性
- 并发场景必须使用数据库锁，防止竞态条件
- 所有 API 端点必须进行权限验证
- 通知发送失败不应影响核心业务逻辑
- 推荐系统调用应在登录和打卡时异步执行，不阻塞用户体验
