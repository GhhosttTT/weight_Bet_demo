# 需求文档: 减肥对赌 APP

## 简介

减肥对赌 APP 是一款基于对赌机制的减肥激励应用。用户可以与好友创建减肥对赌计划,通过金钱激励和社交监督帮助自己达成减肥目标。系统支持 Android 和 iOS 双平台,共享统一的后端 API,确保跨平台数据互通。

## 术语表

- **System**: 减肥对赌 APP 系统(包括移动客户端和后端服务)
- **User**: 已注册并登录的应用用户
- **Creator**: 创建对赌计划的用户
- **Participant**: 接受并参与对赌计划的用户
- **BettingPlan**: 对赌计划,包含双方的减肥目标和赌金信息
- **CheckIn**: 用户每日打卡记录,包含体重数据
- **Settlement**: 计划到期后的结算记录
- **FrozenFunds**: 冻结资金,用户参与计划时冻结的赌金
- **Platform**: 应用平台(Android 或 iOS)

## 需求

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
