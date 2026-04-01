# 合并需求文档

## 概述

本文档合并了减肥对赌 APP 的所有需求，包括：
- 核心应用功能需求
- 好友邀请和计划放弃功能需求
- 充值后余额未更新 Bug 修复需求
- 健身推荐系统需求

---

## 第一部分：核心应用需求

### 需求 1: 用户注册与认证

**用户故事**: 作为新用户,我想要注册账户并登录,以便使用应用的各项功能。

#### 验收标准

1. WHEN 用户提供有效的邮箱地址和密码 THEN THE System SHALL 创建新用户账户并返回成功响应
2. WHEN 用户提供的邮箱已被注册 THEN THE System SHALL 拒绝注册并返回错误提示
3. WHEN 用户使用正确的凭证登录 THEN THE System SHALL 生成 JWT 令牌并返回用户信息
4. WHEN 用户使用错误的凭证登录 THEN THE System SHALL 拒绝登录并返回错误提示
5. WHEN 用户选择 Google 第三方登录 THEN THE System SHALL 通过 OAuth 流程完成认证并创建或关联账户
6. WHEN 用户的访问令牌过期 THEN THE System SHALL 接受刷新令牌并返回新的访问令牌
7. THE System SHALL 对密码进行哈希加密存储

### 需求 2: 用户个人信息管理

**用户故事**: 作为用户,我想要管理我的个人信息,以便系统能够提供个性化的服务。

#### 验收标准

1. WHEN 用户请求查看个人信息 THEN THE System SHALL 返回用户的昵称、性别、年龄、身高、当前体重和目标体重
2. WHEN 用户更新个人信息 THEN THE System SHALL 验证数据有效性并保存更新
3. WHEN 用户提供的身高不在 100-250 cm 范围内 THEN THE System SHALL 拒绝更新并返回验证错误
4. WHEN 用户提供的体重不在 30-300 kg 范围内 THEN THE System SHALL 拒绝更新并返回验证错误
5. WHEN 用户提供的年龄不在 13-120 范围内 THEN THE System SHALL 拒绝更新并返回验证错误
6. WHEN 用户绑定支付方式 THEN THE System SHALL 验证支付方式有效性并保存绑定关系
7. THE System SHALL 为每个用户维护创建时间和最后更新时间

### 需求 3: 创建对赌计划

**用户故事**: 作为用户,我想要创建减肥对赌计划,以便邀请他人与我一起减肥。

#### 验收标准

1. WHEN 用户提供有效的计划参数(赌金、开始日期、结束日期、初始体重、目标体重) THEN THE System SHALL 创建新的对赌计划
2. WHEN 用户提供的赌金金额小于或等于 0 THEN THE System SHALL 拒绝创建并返回验证错误
3. WHEN 用户提供的结束日期早于或等于开始日期 THEN THE System SHALL 拒绝创建并返回验证错误
4. WHEN 用户提供的计划时长超过 365 天 THEN THE System SHALL 拒绝创建并返回验证错误
5. WHEN 用户账户余额小于赌金金额 THEN THE System SHALL 拒绝创建并返回余额不足错误
6. WHEN 计划创建成功 THEN THE System SHALL 冻结创建者的赌金金额
7. WHEN 计划创建成功 THEN THE System SHALL 将计划状态设置为 pending
8. WHEN 创建计划时指定了邀请对象 THEN THE System SHALL 向被邀请用户发送邀请通知
9. THE System SHALL 为每个计划生成唯一标识符
10. THE System SHALL 记录计划创建时间

### 需求 4: 接受对赌计划

**用户故事**: 作为被邀请用户,我想要查看并接受对赌计划,以便与创建者一起减肥。

#### 验收标准

1. WHEN 用户请求查看计划详情 THEN THE System SHALL 返回完整的计划信息(包括赌金、时间、创建者目标)
2. WHEN 用户接受处于 pending 状态的计划 THEN THE System SHALL 验证用户余额并冻结赌金
3. WHEN 用户接受计划但余额不足 THEN THE System SHALL 拒绝接受并返回余额不足错误
4. WHEN 计划创建者尝试接受自己的计划 THEN THE System SHALL 拒绝操作并返回权限错误
5. WHEN 用户尝试接受非 pending 状态的计划 THEN THE System SHALL 拒绝操作并返回状态错误
6. WHEN 用户成功接受计划 THEN THE System SHALL 将计划状态更新为 active
7. WHEN 用户成功接受计划 THEN THE System SHALL 设置计划激活时间
8. WHEN 用户成功接受计划 THEN THE System SHALL 向双方发送计划生效通知
9. WHEN 用户拒绝计划 THEN THE System SHALL 将计划状态更新为 rejected 并解冻创建者赌金
10. WHEN 用户取消未生效的计划 THEN THE System SHALL 将计划状态更新为 cancelled 并解冻创建者赌金

### 需求 5: 每日打卡

**用户故事**: 作为计划参与者,我想要每日打卡记录体重,以便跟踪我的减肥进度。

#### 验收标准

1. WHEN 用户在计划期间内提交打卡数据 THEN THE System SHALL 验证数据并创建打卡记录
2. WHEN 用户提交的体重不在 30-300 kg 范围内 THEN THE System SHALL 拒绝打卡并返回验证错误
3. WHEN 用户在同一天内重复打卡 THEN THE System SHALL 拒绝打卡并返回重复打卡错误
4. WHEN 用户在计划开始日期之前或结束日期之后打卡 THEN THE System SHALL 拒绝打卡并返回日期错误
5. WHEN 用户提交的体重与上次打卡相比单日变化超过 2kg THEN THE System SHALL 将打卡标记为待审核状态
6. WHEN 用户上传体重秤照片 THEN THE System SHALL 存储照片 URL 并关联到打卡记录
7. WHEN 打卡数据通过验证 THEN THE System SHALL 将打卡状态设置为 approved
8. THE System SHALL 记录每次打卡的创建时间
9. THE System SHALL 允许对方用户审核打卡记录

### 需求 6: 进度跟踪

**用户故事**: 作为计划参与者,我想要查看我的减肥进度,以便了解距离目标还有多远。

#### 验收标准

1. WHEN 用户请求查看进度统计 THEN THE System SHALL 返回当前体重、初始体重、目标体重、已减重量和进度百分比
2. WHEN 用户没有任何打卡记录 THEN THE System SHALL 返回进度百分比为 0 且当前体重等于初始体重
3. WHEN 计算进度百分比 THEN THE System SHALL 使用公式 (已减重量 / 目标减重量) × 100
4. WHEN 计算的进度百分比小于 0 THEN THE System SHALL 返回 0
5. WHEN 计算的进度百分比大于 100 THEN THE System SHALL 返回 100
6. THE System SHALL 返回打卡次数统计
7. THE System SHALL 返回距离计划结束的剩余天数
8. THE System SHALL 基于最新的打卡记录计算当前体重

### 需求 7: 自动结算

**用户故事**: 作为计划参与者,我想要在计划到期后自动结算,以便获得应得的奖励。

#### 验收标准

1. WHEN 计划到达结束日期 THEN THE System SHALL 自动触发结算流程
2. WHEN 执行结算时双方都有打卡记录 THEN THE System SHALL 获取双方最终体重并计算实际减重量
3. WHEN 执行结算时一方或双方没有打卡记录 THEN THE System SHALL 将该方视为未达成目标
4. WHEN 双方都达成减重目标 THEN THE System SHALL 向双方各返还原赌金且不收取手续费
5. WHEN 双方都未达成减重目标 THEN THE System SHALL 扣除 10% 手续费后平分剩余金额返还双方
6. WHEN 仅创建者达成目标 THEN THE System SHALL 将全部赌金(双倍)转给创建者且不收取手续费
7. WHEN 仅参与者达成目标 THEN THE System SHALL 将全部赌金(双倍)转给参与者且不收取手续费
8. WHEN 结算完成 THEN THE System SHALL 解冻双方的冻结资金
9. WHEN 结算完成 THEN THE System SHALL 将计划状态更新为 completed
10. WHEN 结算完成 THEN THE System SHALL 创建结算记录并保存结算详情
11. WHEN 结算完成 THEN THE System SHALL 向双方发送结算通知
12. THE System SHALL 确保结算金额总和(创建者金额 + 参与者金额 + 平台手续费)等于双倍赌金

### 需求 8: 资金管理

**用户故事**: 作为用户,我想要管理我的账户资金,以便参与对赌和提现收益。

#### 验收标准

1. WHEN 用户请求查看账户余额 THEN THE System SHALL 返回可用余额和冻结余额
2. WHEN 系统冻结用户资金 THEN THE System SHALL 减少可用余额并增加冻结余额相同金额
3. WHEN 系统解冻用户资金 THEN THE System SHALL 减少冻结余额并增加可用余额相同金额
4. WHEN 系统执行资金转账 THEN THE System SHALL 减少付款方可用余额并增加收款方可用余额相同金额
5. WHEN 用户请求提现 THEN THE System SHALL 验证可用余额是否充足
6. WHEN 用户可用余额不足以支付提现金额 THEN THE System SHALL 拒绝提现并返回余额不足错误
7. THE System SHALL 为每笔资金操作创建交易记录
8. THE System SHALL 记录交易类型(冻结、解冻、转账、提现、退款)
9. THE System SHALL 记录交易状态(处理中、已完成、失败)
10. THE System SHALL 关联交易记录到相关的计划或结算

### 需求 9: 支付集成

**用户故事**: 作为用户,我想要通过第三方支付充值,以便参与对赌计划。

#### 验收标准

1. WHEN 用户发起充值请求 THEN THE System SHALL 调用第三方支付网关创建支付订单
2. WHEN 支付网关返回成功回调 THEN THE System SHALL 增加用户可用余额
3. WHEN 支付网关返回失败回调 THEN THE System SHALL 不改变用户余额并记录失败原因
4. WHEN 支付处理超时 THEN THE System SHALL 标记交易为失败状态
5. THE System SHALL 使用 HTTPS 加密所有支付通信
6. THE System SHALL 验证支付回调的签名以防止伪造
7. THE System SHALL 实现幂等性以防止重复处理同一支付回调

### 需求 10: 通知系统

**用户故事**: 作为用户,我想要接收重要事件的通知,以便及时了解计划状态变化。

#### 验收标准

1. WHEN 用户收到计划邀请 THEN THE System SHALL 发送推送通知
2. WHEN 计划被接受并生效 THEN THE System SHALL 向双方发送推送通知
3. WHEN 计划结算完成 THEN THE System SHALL 向双方发送结算结果通知
4. WHEN 到达每日打卡时间且用户未打卡 THEN THE System SHALL 发送打卡提醒通知
5. WHERE 用户使用 Android 平台 THEN THE System SHALL 使用 Firebase Cloud Messaging 发送通知
6. WHERE 用户使用 iOS 平台 THEN THE System SHALL 使用 Apple Push Notification Service 发送通知
7. THE System SHALL 在用户授予通知权限后发送推送通知

### 需求 11: 排行榜

**用户故事**: 作为用户,我想要查看排行榜,以便与其他用户比较减肥成果。

#### 验收标准

1. WHEN 用户请求查看减重排行榜 THEN THE System SHALL 返回按总减重量排序的用户列表
2. WHEN 用户请求查看连续打卡排行榜 THEN THE System SHALL 返回按连续打卡天数排序的用户列表
3. WHEN 用户请求查看胜率排行榜 THEN THE System SHALL 返回按对赌胜率排序的用户列表
4. THE System SHALL 限制排行榜返回结果数量(默认前 100 名)
5. THE System SHALL 在排行榜中显示用户昵称和相关统计数据
6. THE System SHALL 定期更新排行榜数据(每 5 分钟)

### 需求 12: 社交互动

**用户故事**: 作为用户,我想要与其他用户互动,以便获得鼓励和支持。

#### 验收标准

1. WHEN 用户对计划发表评论 THEN THE System SHALL 创建评论记录并关联到计划
2. WHEN 用户请求查看计划评论 THEN THE System SHALL 返回按时间倒序排列的评论列表
3. WHEN 用户给其他用户点赞鼓励 THEN THE System SHALL 记录鼓励行为并通知被鼓励用户
4. THE System SHALL 限制评论内容长度(最多 500 字符)
5. THE System SHALL 过滤评论中的敏感词汇

### 需求 13: 勋章系统

**用户故事**: 作为用户,我想要获得成就勋章,以便展示我的减肥成果。

#### 验收标准

1. WHEN 用户首次完成对赌计划 THEN THE System SHALL 授予"初次挑战"勋章
2. WHEN 用户连续打卡 7 天 THEN THE System SHALL 授予"坚持一周"勋章
3. WHEN 用户连续打卡 30 天 THEN THE System SHALL 授予"坚持一月"勋章
4. WHEN 用户累计减重达到 10kg THEN THE System SHALL 授予"减重达人"勋章
5. WHEN 用户对赌胜率达到 80% 且参与计划超过 5 个 THEN THE System SHALL 授予"常胜将军"勋章
6. WHEN 用户请求查看勋章列表 THEN THE System SHALL 返回用户已获得的所有勋章
7. THE System SHALL 在用户获得新勋章时发送通知

### 需求 14: 群组挑战

**用户故事**: 作为用户,我想要创建或参与多人群组挑战,以便与更多人一起减肥。

#### 验收标准

1. WHEN 用户创建群组挑战 THEN THE System SHALL 验证参数并创建群组记录
2. WHEN 用户加入群组挑战 THEN THE System SHALL 验证用户资格并添加到群组成员列表
3. WHEN 群组挑战到达结束日期 THEN THE System SHALL 计算所有成员的达成情况并分配奖金
4. THE System SHALL 限制群组挑战的最大成员数量(默认 10 人)
5. THE System SHALL 要求所有成员在挑战开始前冻结赌金

### 需求 15: 数据隐私与安全

**用户故事**: 作为用户,我想要我的个人数据得到保护,以便安全使用应用。

#### 验收标准

1. THE System SHALL 使用 HTTPS/TLS 加密所有客户端与服务器之间的通信
2. THE System SHALL 使用 bcrypt 或 Argon2 算法哈希存储用户密码
3. THE System SHALL 使用 AES-256 加密存储敏感的支付信息
4. WHEN 用户请求导出个人数据 THEN THE System SHALL 生成包含所有用户数据的文件
5. WHEN 用户请求删除账户 THEN THE System SHALL 删除或匿名化所有个人数据
6. THE System SHALL 实现基于角色的访问控制(RBAC)
7. THE System SHALL 记录所有敏感操作的审计日志

### 需求 16: API 安全与限流

**用户故事**: 作为系统管理员,我想要保护 API 免受滥用,以便确保服务稳定性。

#### 验收标准

1. THE System SHALL 验证每个 API 请求的 JWT 令牌
2. WHEN JWT 令牌无效或过期 THEN THE System SHALL 拒绝请求并返回 401 未授权错误
3. THE System SHALL 对每个用户实施请求限流(每分钟最多 100 个请求)
4. WHEN 用户超过请求限流阈值 THEN THE System SHALL 拒绝请求并返回 429 请求过多错误
5. THE System SHALL 验证所有输入参数以防止 SQL 注入攻击
6. THE System SHALL 对输出内容进行转义以防止 XSS 攻击
7. THE System SHALL 实现 CSRF 保护机制

### 需求 17: 跨平台支持

**用户故事**: 作为用户,我想要在 Android 和 iOS 设备上使用应用,以便在不同设备间切换。

#### 验收标准

1. THE System SHALL 提供 Android 版本的移动应用
2. THE System SHALL 提供 iOS 版本的移动应用
3. THE System SHALL 确保 Android 和 iOS 客户端使用相同的后端 API
4. WHEN 用户在 Android 设备上创建计划 THEN THE System SHALL 允许 iOS 用户查看和参与该计划
5. WHEN 用户在 iOS 设备上打卡 THEN THE System SHALL 同步数据到后端并允许 Android 用户查看
6. THE System SHALL 在两个平台上提供一致的用户体验和功能
7. THE System SHALL 支持用户在不同平台间无缝切换使用

### 需求 18: 离线支持

**用户故事**: 作为用户,我想要在网络不稳定时也能使用部分功能,以便不中断我的使用体验。

#### 验收标准

1. WHEN 用户处于离线状态 THEN THE System SHALL 允许用户查看本地缓存的计划和打卡历史
2. WHEN 用户在离线状态下创建打卡记录 THEN THE System SHALL 将数据保存到本地队列
3. WHEN 网络连接恢复 THEN THE System SHALL 自动同步本地队列中的打卡记录到服务器
4. WHEN 同步过程中发生冲突 THEN THE System SHALL 以服务器数据为准并通知用户
5. THE System SHALL 缓存用户个人信息和活跃计划数据到本地存储

### 需求 19: 性能要求

**用户故事**: 作为用户,我想要应用响应迅速,以便获得流畅的使用体验。

#### 验收标准

1. THE System SHALL 在 200ms 内响应 95% 的 API 请求
2. THE System SHALL 在 500ms 内完成打卡操作
3. THE System SHALL 在 1 秒内完成结算计算
4. THE System SHALL 支持至少 10,000 个并发用户
5. THE System SHALL 在 100ms 内完成数据库查询操作
6. THE System SHALL 使用缓存机制减少数据库查询次数
7. THE System SHALL 使用 CDN 加速静态资源加载

### 需求 20: 错误处理与恢复

**用户故事**: 作为用户,我想要在发生错误时得到清晰的提示,以便知道如何解决问题。

#### 验收标准

1. WHEN 发生网络超时 THEN THE System SHALL 显示友好的错误提示并提供重试选项
2. WHEN 支付处理失败 THEN THE System SHALL 不改变用户余额并记录失败原因
3. WHEN 支付处理失败 THEN THE System SHALL 自动重试最多 3 次
4. WHEN 结算过程中发生错误 THEN THE System SHALL 回滚所有资金操作并记录错误日志
5. WHEN 用户提交争议 THEN THE System SHALL 创建争议记录并通知管理员
6. THE System SHALL 为所有错误返回明确的错误代码和描述信息
7. THE System SHALL 记录所有错误到日志系统以便排查问题

---

## 第二部分：好友邀请和计划放弃需求

### 需求 21: 邀请好友参与计划

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

### 需求 22: 好友搜索功能

**User Story:** 作为计划创建者，我想通过邮箱搜索好友，以便确认我邀请的是正确的人。

#### Acceptance Criteria

1. WHEN THE Plan_Creator enters an email address, THE Friend_Search_Service SHALL validate the email format
2. IF the email format is invalid, THEN THE Friend_Search_Service SHALL display an error message
3. WHEN a valid email is submitted, THE Friend_Search_Service SHALL query the user database
4. WHEN a matching user is found, THE Friend_Search_Service SHALL return the user's name and age
5. IF no matching user is found, THEN THE Friend_Search_Service SHALL display a "user not found" message

### 需求 23: 计划状态管理

**User Story:** 作为系统管理员，我想系统能够正确管理计划的各种状态，以便准确跟踪计划的生命周期。

#### Acceptance Criteria

1. THE Plan_Status_Manager SHALL support the following states: pending, active, completed, cancelled, rejected, expired
2. WHEN a plan is created, THE Plan_Status_Manager SHALL set the initial status to pending
3. WHEN THE Plan_Participant accepts an invitation, THE Plan_Status_Manager SHALL change the status from pending to active
4. WHEN THE Plan_Participant rejects an invitation, THE Plan_Status_Manager SHALL change the status from pending to rejected
5. WHEN a plan reaches its end date, THE Plan_Status_Manager SHALL evaluate the plan completion
6. IF a plan reaches its end date and is not completed, THEN THE Plan_Status_Manager SHALL change the status to expired
7. WHEN a user abandons a plan, THE Plan_Status_Manager SHALL change the status to cancelled

### 需求 24: 计划过期处理

**User Story:** 作为用户，我想系统能够自动标记过期的计划，以便我知道哪些计划已经超过了截止日期。

#### Acceptance Criteria

1. WHEN a plan's end date is reached, THE Plan_Status_Manager SHALL check if the plan is completed
2. IF the plan status is active and the end date has passed, THEN THE Plan_Status_Manager SHALL change the status to expired
3. WHEN a plan status changes to expired, THE Notification_Service SHALL notify both participants
4. THE Plan_Status_Manager SHALL run the expiration check at least once per day

### 需求 25: 放弃待接受状态的计划

**User Story:** 作为用户，我想在计划还未开始时能够放弃计划，以便在改变主意时取回我的赌金。

#### Acceptance Criteria

1. WHILE a plan status is pending, THE Betting_Plan SHALL display an abandon button
2. WHEN THE Plan_Creator abandons a pending plan, THE Fund_Manager SHALL unfreeze THE Plan_Creator's Stake_Amount
3. WHEN THE Plan_Creator abandons a pending plan, THE Plan_Status_Manager SHALL change the status to cancelled
4. WHEN THE Plan_Participant rejects an invitation, THE Fund_Manager SHALL unfreeze THE Plan_Creator's Stake_Amount
5. WHEN THE Plan_Participant rejects an invitation, THE Plan_Status_Manager SHALL change the status to rejected
6. WHEN a pending plan is abandoned or rejected, THE Notification_Service SHALL notify the other participant

### 需求 26: 放弃进行中的计划

**User Story:** 作为用户，我想在计划进行中时能够放弃计划，但我理解这意味着我将失去赌金。

#### Acceptance Criteria

1. WHILE a plan status is active, THE Betting_Plan SHALL display an abandon button with a warning message
2. WHEN a User abandons an active plan, THE Plan_Status_Manager SHALL mark that User as the losing party
3. WHEN a User abandons an active plan, THE Fund_Manager SHALL transfer the abandoning User's Stake_Amount to the other participant
4. WHEN a User abandons an active plan, THE Fund_Manager SHALL unfreeze and transfer the other participant's Stake_Amount to that participant
5. WHEN an active plan is abandoned, THE Plan_Status_Manager SHALL change the status to cancelled
6. WHEN an active plan is abandoned, THE Notification_Service SHALL notify the winning participant
7. THE Betting_Plan SHALL require confirmation before processing an abandon action on an active plan

### 需求 27: 资金处理的原子性

**User Story:** 作为系统管理员，我想确保所有资金操作都是原子性的，以便避免资金丢失或重复处理。

#### Acceptance Criteria

1. WHEN THE Fund_Manager processes any fund operation, THE Fund_Manager SHALL use database transactions
2. IF a fund operation fails, THEN THE Fund_Manager SHALL roll back all related changes
3. WHEN a fund operation completes, THE Fund_Manager SHALL log the transaction details
4. THE Fund_Manager SHALL ensure that the total amount of frozen and transferred funds equals the original Stake_Amount
5. IF a fund operation is interrupted, THEN THE Fund_Manager SHALL maintain data consistency

### 需求 28: 邀请通知内容

**User Story:** 作为被邀请的用户，我想收到包含完整计划信息的通知，以便我能够做出明智的决定。

#### Acceptance Criteria

1. WHEN an invitation is sent, THE Notification_Service SHALL include the Plan_Creator's name in the notification
2. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's target weight loss goal
3. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's duration
4. WHEN an invitation is sent, THE Notification_Service SHALL include the Stake_Amount
5. WHEN an invitation is sent, THE Notification_Service SHALL include the plan's start and end dates
6. THE Notification_Service SHALL provide a direct link to view the full plan details

### 需求 29: 单元测试覆盖

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

### 需求 30: 邀请状态跟踪

**User Story:** 作为计划创建者，我想知道我的邀请是否已被查看和处理，以便我能够跟进。

#### Acceptance Criteria

1. WHEN an invitation is sent, THE Invitation_System SHALL record the invitation timestamp
2. WHEN THE Plan_Participant views the invitation, THE Invitation_System SHALL record the view timestamp
3. WHEN THE Plan_Participant responds to the invitation, THE Invitation_System SHALL record the response timestamp
4. THE Invitation_System SHALL allow THE Plan_Creator to view the invitation status
5. THE Invitation_System SHALL display whether the invitation is pending, viewed, accepted, or rejected

### 需求 31: 并发邀请处理

**User Story:** 作为系统管理员，我想确保系统能够正确处理同一用户的多个邀请，以便避免冲突和数据不一致。

#### Acceptance Criteria

1. WHEN multiple invitations are sent to the same User, THE Invitation_System SHALL allow THE User to view all pending invitations
2. THE Invitation_System SHALL allow THE User to accept or reject each invitation independently
3. WHEN THE User accepts an invitation, THE Invitation_System SHALL not automatically reject other pending invitations
4. THE Invitation_System SHALL use database locking to prevent race conditions when processing invitation responses
5. IF two users simultaneously try to accept invitations that would exceed their available balance, THEN THE Fund_Manager SHALL process them sequentially and reject the second if insufficient funds exist

### 需求 32: 邀请验证规则

**User Story:** 作为系统管理员，我想确保邀请遵循业务规则，以便维护系统的完整性。

#### Acceptance Criteria

1. WHEN THE Plan_Creator attempts to send an invitation, THE Invitation_System SHALL verify that THE Plan_Creator has sufficient frozen funds
2. THE Invitation_System SHALL prevent THE Plan_Creator from inviting themselves
3. THE Invitation_System SHALL prevent duplicate invitations for the same plan
4. WHEN THE Plan_Participant attempts to accept an invitation, THE Invitation_System SHALL verify that THE Plan_Participant has sufficient balance to freeze the Stake_Amount
5. IF THE Plan_Participant has insufficient balance, THEN THE Invitation_System SHALL display an error message and prevent acceptance

---

## 第三部分：充值后余额未更新 Bug 修复需求

### Bug 分析

#### 当前行为 (缺陷)

1.1 WHEN 用户充值成功(充值接口返回 {"success":true,"message":"充值成功","amount":200.0}) THEN 系统未更新用户余额,余额仍为充值前的值(0.0元)

1.2 WHEN 用户在充值成功后立即创建赌注计划 THEN 系统仍然检查到余额不足(0.0 < 200.0),返回402错误:"余额不足,需要充值 200.0 元"

1.3 WHEN 充值接口返回成功响应 THEN 系统未将充值金额添加到用户的可用余额中

#### 期望行为 (正确)

2.1 WHEN 用户充值成功(充值接口返回 {"success":true,"message":"充值成功","amount":200.0}) THEN 系统 SHALL 立即更新用户余额,将充值金额添加到用户的可用余额中

2.2 WHEN 用户在充值成功后立即创建赌注计划 THEN 系统 SHALL 检查到余额充足(200.0 >= 200.0),成功创建计划并冻结相应金额

2.3 WHEN 充值接口返回成功响应 THEN 系统 SHALL 在数据库中持久化更新后的用户余额,确保后续查询能获取到最新余额

2.4 WHEN 充值操作完成 THEN 系统 SHALL 创建一条交易记录,记录充值金额和时间

#### 不变行为 (回归预防)

3.1 WHEN 用户余额充足时创建赌注计划 THEN 系统 SHALL CONTINUE TO 成功冻结赌金并创建计划

3.2 WHEN 用户余额不足且未充值时创建赌注计划 THEN 系统 SHALL CONTINUE TO 返回余额不足错误

3.3 WHEN 充值失败(充值接口返回失败响应) THEN 系统 SHALL CONTINUE TO 不更新用户余额

3.4 WHEN 用户查询账户余额 THEN 系统 SHALL CONTINUE TO 返回准确的可用余额和冻结余额

3.5 WHEN 系统执行结算转账操作 THEN 系统 SHALL CONTINUE TO 正确更新用户余额

3.6 WHEN 用户提现操作 THEN 系统 SHALL CONTINUE TO 正确扣减用户可用余额

---

## 第四部分：健身推荐系统需求

### 产品概述

#### 产品定位
- **非对话型**：不做开放式聊天，只做结构化推荐
- **输入驱动**：用户输入体重数据 → 系统输出今日推荐
- **本地优先**：模型本地部署，数据后端管理

#### 核心场景

| 场景 | 用户行为 | 系统响应 |
|------|---------|---------|
| 健康教练初始化 | 用户登录时| 结合用户体重数据，返回今日训练+饮食建议 |
| 健康教练 | 用户打卡| 结合用户体重数据，返回今日训练+饮食建议 |

### 功能模块

#### 模块A：用户数据管理（后端）

**职责**：存储、查询、计算用户数据

| 功能 | 说明 |
|------|------|
| 用户档案 | 身高、初始体重、目标体重 |
| 打卡记录 | 运动类型、时长、日期、结合用户身高数据算出最新的BMI|
| 趋势计算 | 周环比、月环比、平台期检测 |

**调用方式**：采取登录初始化、打卡时更新用户数据的调用方式，确保用户不用等待模型返回推荐结果，所以返回的数据需要临时存储

---

## 术语表

### 核心应用术语
- **System**: 减肥对赌 APP 系统(包括移动客户端和后端服务)
- **User**: 已注册并登录的应用用户
- **Creator**: 创建对赌计划的用户
- **Participant**: 接受并参与对赌计划的用户
- **BettingPlan**: 对赌计划,包含双方的减肥目标和赌金信息
- **CheckIn**: 用户每日打卡记录,包含体重数据
- **Settlement**: 计划到期后的结算记录
- **FrozenFunds**: 冻结资金,用户参与计划时冻结的赌金
- **Platform**: 应用平台(Android 或 iOS)

### 邀请和计划放弃术语
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

### Bugfix 术语
- **Bug_Condition (C)**: 充值成功但余额未更新的条件 - 当充值接口返回成功响应但数据库中的用户余额未增加充值金额
- **Property (P)**: 充值成功后的期望行为 - 用户的可用余额应立即增加充值金额,并在数据库中持久化
- **Preservation**: 其他余额操作(冻结、解冻、转账、提现)和余额查询功能必须保持不变
- **charge()**: PaymentRepository 中的充值方法,调用后端 API `/api/payments/charge`
- **getBalance()**: UserRepository 中的获取余额方法,调用后端 API `/api/users/{userId}/balance`
- **availableBalance**: 用户可用余额,可以用于创建赌注计划或提现
- **frozenBalance**: 用户冻结余额,参与活跃计划时被冻结的资金
- **CacheManager**: 本地缓存管理器,缓存用户信息以减少网络请求
