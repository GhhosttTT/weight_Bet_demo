# 减肥对赌 APP - 设计文档

## 1. 概述

### 1.1 核心价值
减肥对赌 APP 是一款基于"对赌 + 监督 + 奖励机制"的减肥应用，通过经济约束和社交监督帮助用户坚持减肥计划。

**核心机制**：
- 💰 经济激励：双方缴纳赌金，达成目标者获胜
- 👥 社交监督：好友互相对赌，相互督促
- 🏆 公平结算：透明规则，自动执行

### 1.2 技术架构
- **前端**: Android + iOS
- **后端**: FastAPI (Python) +  SQLite  + Redis
- **认证**: JWT Token + Firebase Auth
- **支付**: Stripe / PayPal

## 2. 系统架构

### 2.1 三层架构图

```
┌─────────────────┐
│  Flutter 移动端  │
│  (Android/iOS)  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼         ▼          ▼
┌──────┐  ┌──────┐  ┌────────┐  ┌──────┐  ┌──────┐  ┌────────┐
│认证  │  │用户  │  │对赌计划│  │打卡  │  │支付  │  │结算    │
│服务  │  │服务  │  │服务    │  │服务  │  │服务  │  │服务    │
└──┬───┘  └──┬───┘  └───┬────┘  └──┬───┘  └──┬───┘  └───┬────┘
   │         │         │          │         │          │
   ▼         ▼         ▼          ▼         ▼          ▼
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │用户数据库│  │计划数据库│  │支付数据库│  │社交库  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
│  ┌──────────┐  ┌──────────┐                             │
│  │ Redis    │  │ S3       │                             │
│  │ 缓存     │  │ 文件存储  │                             │
│  └──────────┘  └──────────┘                             │
└─────────────────────────────────────────────────────────┘
```

## 3. 核心业务流程

### 1. 对赌计划创建与接受流程

```mermaid
sequenceDiagram
    participant A as 用户A
    participant App as 移动客户端
    participant API as 后端API
    participant Pay as 支付服务
    participant Gateway as 支付网关
    participant B as 用户B
    
    A->>App: 创建减肥计划
    App->>API: POST /betting-plans
    API->>API: 验证计划参数
    API->>Pay: 检查用户A余额
    
    alt 余额充足
        API->>Pay: 冻结用户A赌金
        Pay-->>API: 冻结成功
        API-->>App: 返回计划ID
    else 余额不足
        Pay-->>API: 余额不足
        API-->>App: 返回需要充值(金额)
        App->>Gateway: 调起支付充值
        Gateway-->>App: 充值成功
        App->>API: POST /betting-plans (重试)
        API->>Pay: 冻结用户A赌金
        Pay-->>API: 冻结成功
        API-->>App: 返回计划ID
    end
    
    App->>App: 跳转到邀请好友界面
    A->>App: 搜索好友并发送邀请
    App->>API: POST /betting-plans/{id}/invite
    API->>B: 发送邀请通知
    
    B->>App: 进入App后弹窗提示打开计划详情
    App->>API: GET /betting-plans/{id}
    
#### 3.1.2 邀请与一次性弹窗机制

**设计要点**：
- 弹窗触发范围：仅针对**尚未进行中的计划**（状态为 `pending` 或 `waiting_double_check`）
- 对于已接受（`active`）或已 double-check 过的计划，不再弹出提示
- 后端根据计划状态筛选待处理项，避免重复提示
- 前端使用 SharedPreferences 记录已显示的弹窗，确保每种弹窗只显示一次

**弹窗触发条件**：
1. **邀请弹窗**：仅当邀请状态为 `pending` 且计划状态为 `pending` 时触发
2. **Double-Check 弹窗**：仅当计划状态为 `waiting_double_check` 时触发
3. **结算弹窗**：仅当计划状态为 `active` 且已到期尚未结算时触发

**相关接口**：
```yaml
GET /me/pending-actions:
  description: 检查一次性邀请/待确认事项（仅返回未处理计划）
  response:
    invitations: [{id, planId, fromUserId, message, type, isFirstTime}]
      # 仅返回 status == pending 的邀请
    doubleChecks: [{planId, initiatorId, reason, isPending}]
      # 仅返回 status == waiting_double_check 的计划
    settlements: [{planId, isPending}]
      # 仅返回 status == active 且已到期未结算的计划
```

#### 1.3 Double-Check 确认流程

```
用户 B 接受计划 → 提交目标 → 设置待确认标志 → 
用户 A 登录收到提示 → 进入 double-check 界面 → 
选择确认/撤销 → 更新计划状态
```
    
    API-->>App: 返回完整计划信息
    B->>App: B编写针对自己的计划
    App->>API: POST /betting-plans/{id}/accept
    API->>Pay: 检查用户B余额
    
    alt 余额充足
        API->>Pay: 冻结用户B赌金
        Pay-->>API: 冻结成功
        API->>API: 激活计划
    else 余额不足
        Pay-->>API: 余额不足
        API-->>App: 返回需要充值(金额)
        App->>Gateway: 调起支付充值
        Gateway-->>App: 充值成功
        App->>API: POST /betting-plans/{id}/accept (重试)
        API->>Pay: 冻结用户B赌金
        Pay-->>API: 冻结成功
        API->>API: 激活计划
    
    A->>App: 跳转到计划详情界面 查看B计划是否合理，不合理可以撤销计划（双方的冻结金额原路返还 当作两个人都成功了）同意的话计划生效
    API->>B: 发送计划生效通知
    end
    
    
```


### 打卡与结算流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant App as 移动客户端
    participant API as 后端API
    participant Scheduler as 定时调度器
    participant Settlement as 结算服务
    
    
    Note over Scheduler: 计划到期时间
    Scheduler->>Settlement: 触发结算弹窗点击确认结算进入订单界面
    Settlement->>API: GET /betting-plans/{id}
    API-->>Settlement: 返回计划数据
    Settlement->>Settlement: 应用结算规则
    participant A as 用户A
    participant AppA as 移动客户端A
    participant API as 后端API
    participant AppB as 移动客户端B
    participant B as 用户B
    
    Note over API: 计划到期日 0:00
    API->>AppA: 推送结算通知
    API->>AppB: 推送结算通知
    
    A->>AppA: 打开计划详情
    AppA->>API: 获取结算状态
    API-->>AppA: 返回待结算
    A->>AppA: 点击"我达成了"+"对方未达成"
    AppA->>API: 提交选择
    API->>API: 记录A选择并锁定
    API-->>AppA: 提交成功等待对方
    
    B->>AppB: 打开计划详情
    AppB->>API: 获取结算状态
    API-->>AppB: 返回待结算
    B->>AppB: 点击"我未达成"+"对方达成"
    AppB->>API: 提交选择
    API->>API: 记录B选择并锁定
    
    API->>API: 比对双方选择
    Note right of API: A:我成对方败<br/>B:我败对方成<br/>匹配成功 A获胜
    
    API->>Pay: 解冻并划转资金
    Pay->>Pay: A保证金返还A<br/>B保证金划转给A
    Pay-->>API: 划转完成
    
    API->>AppA: 推送结算结果
    API->>AppB: 推送结算结果
    
    AppA->>A: 显示"你赢了"<br/>获得双方全部保证金
    AppB->>B: 显示"你输了"<br/>保证金已给对方
    
    alt 双方选择不匹配
        A->>AppA: 点击"我达成了"+"对方达成了"
        AppA->>API: 提交选择
        B->>AppB: 点击"我达成了"+"对方未达成"
        AppB->>API: 提交选择
        API->>API: 比对失败<br/>A选双双成<br/>B选我成对方败
        API->>API: 标记当日无效<br/>延期一天
        API->>AppA: 通知不匹配明日再选
        API->>AppB: 通知不匹配明日再选
        
        Note over API: 次日 0:00 第二次机会
        API->>AppA: 推送第二次结算通知
        API->>AppB: 推送第二次结算通知
        
        A->>AppA: 点击"我达成了"+"对方未达成"
        B->>AppB: 点击"我未达成"+"对方达成了"
        API->>API: 比对成功<br/>A获胜
        
        API->>Pay: 解冻并划转
        Pay-->>API: 完成
        API->>AppA: 推送胜利结果
        API->>AppB: 推送失败结果
    end
    
    alt 三次均不匹配进入强制仲裁
        API->>API: 第三次不匹配<br/>触发强制仲裁
        API->>AppA: 推送仲裁通知<br/>要求视频称重
        API->>AppB: 推送仲裁通知<br/>要求视频称重
        
        A->>AppA: 进入视频称重
        AppA->>API: 上传实时视频+体重数据
        B->>AppB: 进入视频称重
        AppB->>API: 上传实时视频+体重数据
        
        API->>API: 审核双方数据
        Note right of API: A达成 B未达成
        
        API->>Pay: 扣除15%仲裁费<br/>剩余85%给A
        Pay->>Pay: A拿回原保证金<br/>B的85%给A<br/>15%平台扣留
        Pay-->>API: 完成
        
        API->>AppA: 推送仲裁胜利<br/>获得85%
        API->>AppB: 推送仲裁失败<br/>归零
    end
    
    alt 双双达成
        A->>AppA: 点击"我达成了"+"对方达成了"
        B->>AppB: 点击"我达成了"+"对方达成了"
        API->>API: 比对成功<br/>双双达成
        API->>Pay: 双方保证金原路返还
        Pay-->>API: 完成
        API->>AppA: 推送双双成功<br/>全额返还
        API->>AppB: 推送双双成功<br/>全额返还
    end
    
    alt 双双未达成
        A->>AppA: 点击"我未达成"+"对方未达成"
        B->>AppB: 点击"我未达成"+"对方未达成"
        API->>API: 比对成功<br/>双双未达成
        API->>Pay: 扣除10%平台费<br/>剩余90%平分
        Pay->>Pay: 双方各拿45%
        Pay-->>API: 完成
        API->>AppA: 推送双双失败<br/>各返45%
        API->>AppB: 推送双双失败<br/>各返45%
    end
    
    alt 任一方超时未选
        Note over API: 24小时倒计时结束
        API->>API: 检测A已选B未选
        API->>API: 标记当日无效<br/>延期一天
        API->>AppA: 通知对方超时<br/>明日再选
        API->>AppB: 推送超时提醒<br/>已丧失本次机会
    Settlement->>API: POST /settlements
    API->>User: 发送结算通知
```

## 组件和接口

### 组件 1: 认证服务 (AuthService)

**目的**: 处理用户注册、登录、身份验证和授权

**接口**:
```dart
abstract class AuthService {
  /// 用户注册
  Future<AuthResult> register(RegisterRequest request);
  
  /// 用户登录
  Future<AuthResult> login(LoginRequest request);
  
  /// 第三方登录 (Google)
  Future<AuthResult> loginWithThirdParty(ThirdPartyProvider provider);
  
  /// 刷新访问令牌
  Future<TokenResult> refreshToken(String refreshToken);
  
  /// 登出
  Future<void> logout(String userId);
  
  /// 验证令牌
  Future<bool> validateToken(String token);
}
```

**职责**:
- 处理用户注册和登录请求
- 生成和验证 JWT 令牌
- 管理用户会话
- 集成第三方认证提供商

### 组件 2: 用户服务 (UserService)

**目的**: 管理用户个人信息和配置

**接口**:
```dart
abstract class UserService {
  /// 获取用户信息
  Future<User> getUserProfile(String userId);
  
  /// 更新用户信息
  Future<User> updateUserProfile(String userId, UserProfileUpdate update);
  
  /// 绑定支付方式
  Future<void> bindPaymentMethod(String userId, PaymentMethod method);
  
  /// 获取用户统计数据
  Future<UserStats> getUserStats(String userId);
}
```

**职责**:
- 管理用户个人资料
- 处理用户信息更新
- 管理支付方式绑定
- 提供用户统计数据


### 组件 3: 对赌计划服务 (BettingPlanService)

**目的**: 管理减肥对赌计划的创建、邀请、接受和状态管理

**接口**:
```dart
abstract class BettingPlanService {
  /// 创建对赌计划
  Future<BettingPlan> createPlan(String userId, CreatePlanRequest request);
  
  /// 邀请对方参与
  Future<void> inviteParticipant(String planId, String inviteeId);
  
  /// 接受对赌计划
  Future<BettingPlan> acceptPlan(String planId, String userId, AcceptPlanRequest request);
  
  /// 拒绝对赌计划
  Future<void> rejectPlan(String planId, String userId);
  
  /// 获取计划详情
  Future<BettingPlan> getPlanDetails(String planId);
  
  /// 获取用户的所有计划
  Future<List<BettingPlan>> getUserPlans(String userId, PlanStatus? status);
  
  /// 取消计划 (仅限未生效的计划)
  Future<void> cancelPlan(String planId, String userId);
}
```

**职责**:
- 创建和管理对赌计划
- 处理邀请和接受流程
- 验证计划参数的合理性
- 管理计划状态转换

### 组件 4: 打卡服务 (CheckInService)

**目的**: 处理用户每日打卡和体重数据记录

**接口**:
```dart
abstract class CheckInService {
  /// 创建打卡记录
  Future<CheckIn> createCheckIn(String userId, String planId, CheckInData data);
  
  /// 获取打卡历史
  Future<List<CheckIn>> getCheckInHistory(String planId, String userId);
  
  /// 审核打卡数据
  Future<void> reviewCheckIn(String checkInId, String reviewerId, ReviewResult result);
  
  /// 获取进度统计
  Future<ProgressStats> getProgress(String planId, String userId);
  
  /// 验证打卡数据真实性
  Future<ValidationResult> validateCheckInData(CheckInData data);
}
```

**职责**:
- 记录用户每日体重数据
- 验证打卡数据的真实性
- 提供进度跟踪和可视化
- 支持对方审核机制

### 组件 5: 支付服务 (PaymentService)

**目的**: 处理资金冻结、解冻和转账

**接口**:
```dart
abstract class PaymentService {
  /// 冻结赌金
  Future<FreezeResult> freezeFunds(String userId, String planId, double amount);
  
  /// 解冻赌金
  Future<void> unfreezeFunds(String userId, String planId);
  
  /// 转账
  Future<TransferResult> transferFunds(String fromUserId, String toUserId, double amount);
  
  /// 提现
  Future<WithdrawResult> withdraw(String userId, double amount);
  
  /// 获取账户余额
  Future<Balance> getBalance(String userId);
  
  /// 获取交易历史
  Future<List<Transaction>> getTransactionHistory(String userId);
}
```

**职责**:
- 与第三方支付网关集成
- 管理用户资金冻结和解冻
- 处理资金转账和提现
- 确保支付安全和数据加密


### 组件 6: 结算服务 (SettlementService)

**目的**: 在计划结束时自动计算和执行结算

**接口**:
```dart
abstract class SettlementService {
  /// 执行结算
  Future<Settlement> executeSettlement(String planId);
  
  /// 计算结算结果
  Future<SettlementResult> calculateSettlement(String planId);
  
  /// 获取结算详情
  Future<Settlement> getSettlementDetails(String settlementId);
  
  /// 处理争议
  Future<void> handleDispute(String settlementId, DisputeRequest request);
}
```

**职责**:
- 在计划到期时自动触发结算
- 根据规则计算双方的结算金额
- 执行资金转移
- 生成结算明细记录

### 组件 7: 社交服务 (SocialService)

**目的**: 提供社交互动功能,包括排行榜、评论、勋章等

**接口**:
```dart
abstract class SocialService {
  /// 获取排行榜
  Future<List<LeaderboardEntry>> getLeaderboard(LeaderboardType type, int limit);
  
  /// 发表评论
  Future<Comment> postComment(String planId, String userId, String content);
  
  /// 获取评论列表
  Future<List<Comment>> getComments(String planId);
  
  /// 点赞/鼓励
  Future<void> encourageUser(String userId, String targetUserId);
  
  /// 获取用户勋章
  Future<List<Badge>> getUserBadges(String userId);
  
  /// 创建群组挑战
  Future<GroupChallenge> createGroupChallenge(String creatorId, GroupChallengeRequest request);
  
  /// 加入群组挑战
  Future<void> joinGroupChallenge(String challengeId, String userId);
}
```

**职责**:
- 管理排行榜和竞争机制
- 处理用户评论和互动
- 管理勋章和成就系统
- 支持多人群组挑战

## 数据模型

### 模型 1: User (用户)

```dart
class User {
  final String id;
  final String email;
  final String? phoneNumber;
  final String nickname;
  final Gender gender;
  final int age;
  final double height; // 单位: cm
  final double currentWeight; // 单位: kg
  final double? targetWeight; // 单位: kg
  final PaymentMethod? paymentMethod;
  final DateTime createdAt;
  final DateTime updatedAt;
}

enum Gender { male, female, other }
```

**验证规则**:
- email 必须符合邮箱格式
- phoneNumber 必须符合国际电话号码格式
- nickname 长度 2-20 字符
- age 必须在 13-120 之间
- height 必须在 100-250 cm 之间
- currentWeight 必须在 30-300 kg 之间
- targetWeight 如果设置,必须在 30-300 kg 之间


### 模型 2: BettingPlan (对赌计划)

```dart
class BettingPlan {
  final String id;
  final String creatorId;
  final String? participantId;
  final PlanStatus status;
  final double betAmount; // 赌金金额
  final DateTime startDate;
  final DateTime endDate;
  final String? description;
  final CreatorGoal creatorGoal;
  final ParticipantGoal? participantGoal;
  final DateTime createdAt;
  final DateTime? activatedAt;
}

class CreatorGoal {
  final double initialWeight;
  final double targetWeight;
  final double targetWeightLoss; // 目标减重量
}

class ParticipantGoal {
  final double initialWeight;
  final double targetWeight;
  final double targetWeightLoss;
}

enum PlanStatus {
  pending,      // 等待对方接受
  active,       // 进行中
  completed,    // 已完成
  cancelled,    // 已取消
  rejected      // 已拒绝
}
```

**验证规则**:
- betAmount 必须大于 0
- endDate 必须晚于 startDate
- 计划时长必须在 1-365 天之间
- initialWeight 和 targetWeight 必须在合理范围内
- targetWeightLoss 必须为正数(减肥)

### 模型 3: CheckIn (打卡记录)

```dart
class CheckIn {
  final String id;
  final String userId;
  final String planId;
  final double weight;
  final DateTime checkInDate;
  final String? photoUrl; // 可选的体重秤照片
  final String? note;
  final ReviewStatus reviewStatus;
  final String? reviewerId;
  final String? reviewComment;
  final DateTime createdAt;
}

enum ReviewStatus {
  pending,    // 待审核
  approved,   // 已通过
  rejected    // 已拒绝
}
```

**验证规则**:
- weight 必须在 30-300 kg 之间
- checkInDate 必须在计划的 startDate 和 endDate 之间
- 每个用户每天只能打卡一次
- photoUrl 如果提供,必须是有效的图片 URL

### 模型 4: Settlement (结算记录)

```dart
class Settlement {
  final String id;
  final String planId;
  final SettlementResult result;
  final double creatorAmount; // 创建者获得金额
  final double participantAmount; // 参与者获得金额
  final double platformFee; // 平台手续费
  final DateTime settlementDate;
  final String? notes;
}

class SettlementResult {
  final bool creatorAchieved; // 创建者是否达成目标
  final bool participantAchieved; // 参与者是否达成目标
  final double creatorFinalWeight;
  final double participantFinalWeight;
  final double creatorWeightLoss;
  final double participantWeightLoss;
}
```

**验证规则**:
- creatorAmount + participantAmount + platformFee 必须等于总赌金的两倍
- platformFee 不能超过总赌金的 10%
- settlementDate 必须在计划 endDate 之后


### 模型 5: Transaction (交易记录)

```dart
class Transaction {
  final String id;
  final String userId;
  final TransactionType type;
  final double amount;
  final TransactionStatus status;
  final String? relatedPlanId;
  final String? relatedSettlementId;
  final DateTime createdAt;
  final DateTime? completedAt;
}

enum TransactionType {
  freeze,      // 冻结
  unfreeze,    // 解冻
  transfer,    // 转账
  withdraw,    // 提现
  refund       // 退款
}

enum TransactionStatus {
  pending,     // 处理中
  completed,   // 已完成
  failed       // 失败
}
```

**验证规则**:
- amount 必须大于 0
- status 为 completed 时必须有 completedAt
- freeze 和 unfreeze 必须关联 planId

## 算法伪代码

### 主算法 1: 创建对赌计划

```dart
Future<BettingPlan> createBettingPlan(String userId, CreatePlanRequest request) async
```

**前置条件**:
- userId 是有效的已注册用户
- request.betAmount > 0
- request.endDate > request.startDate
- request.initialWeight 和 request.targetWeight 在合理范围内
- 用户已绑定支付方式
- 用户账户余额 >= request.betAmount

**后置条件**:
- 返回有效的 BettingPlan 对象
- 计划状态为 PlanStatus.pending
- 用户 A 的赌金已被冻结
- 如果指定了 inviteeId,邀请通知已发送

**循环不变式**: 不适用(无循环)

```pascal
ALGORITHM createBettingPlan(userId, request)
INPUT: userId (String), request (CreatePlanRequest)
OUTPUT: plan (BettingPlan)

BEGIN
  // 前置条件验证
  ASSERT validateUser(userId) = true
  ASSERT request.betAmount > 0
  ASSERT request.endDate > request.startDate
  ASSERT validateWeightRange(request.initialWeight, request.targetWeight) = true
  
  // 步骤 1: 验证用户余额
  balance ← getBalance(userId)
  IF balance < request.betAmount THEN
    THROW InsufficientBalanceError("余额不足")
  END IF
  
  // 步骤 2: 创建计划对象
  plan ← NEW BettingPlan {
    id: generateUUID(),
    creatorId: userId,
    participantId: null,
    status: PlanStatus.pending,
    betAmount: request.betAmount,
    startDate: request.startDate,
    endDate: request.endDate,
    description: request.description,
    creatorGoal: {
      initialWeight: request.initialWeight,
      targetWeight: request.targetWeight,
      targetWeightLoss: request.initialWeight - request.targetWeight
    },
    participantGoal: null,
    createdAt: now(),
    activatedAt: null
  }
  
  // 步骤 3: 冻结创建者赌金
  freezeResult ← freezeFunds(userId, plan.id, request.betAmount)
  IF freezeResult.success = false THEN
    THROW PaymentError("资金冻结失败")
  END IF
  
  // 步骤 4: 保存计划到数据库
  savedPlan ← database.save(plan)
  
  // 步骤 5: 如果指定了邀请对象,发送邀请
  IF request.inviteeId ≠ null THEN
    sendInvitation(plan.id, request.inviteeId)
  END IF
  
  // 后置条件验证
  ASSERT savedPlan.status = PlanStatus.pending
  ASSERT savedPlan.creatorId = userId
  
  RETURN savedPlan
END
```


### 主算法 2: 接受对赌计划

```dart
Future<BettingPlan> acceptBettingPlan(String planId, String userId, AcceptPlanRequest request) async
```

**前置条件**:
- planId 是有效的计划 ID
- userId 是有效的已注册用户
- 计划状态为 PlanStatus.pending
- userId 不是计划创建者
- request.initialWeight 和 request.targetWeight 在合理范围内
- 用户已绑定支付方式
- 用户账户余额 >= plan.betAmount

**后置条件**:
- 返回更新后的 BettingPlan 对象
- 计划状态变为 PlanStatus.active
- 用户 B 的赌金已被冻结
- 计划的 activatedAt 已设置
- 双方都收到计划生效通知

**循环不变式**: 不适用(无循环)

```pascal
ALGORITHM acceptBettingPlan(planId, userId, request)
INPUT: planId (String), userId (String), request (AcceptPlanRequest)
OUTPUT: plan (BettingPlan)

BEGIN
  // 前置条件验证
  ASSERT validateUser(userId) = true
  
  // 步骤 1: 获取计划
  plan ← database.findPlanById(planId)
  IF plan = null THEN
    THROW NotFoundError("计划不存在")
  END IF
  
  // 步骤 2: 验证计划状态和权限
  IF plan.status ≠ PlanStatus.pending THEN
    THROW InvalidStateError("计划状态不允许接受")
  END IF
  
  IF plan.creatorId = userId THEN
    THROW PermissionError("不能接受自己创建的计划")
  END IF
  
  // 步骤 3: 验证用户余额
  balance ← getBalance(userId)
  IF balance < plan.betAmount THEN
    THROW InsufficientBalanceError("余额不足")
  END IF
  
  // 步骤 4: 验证目标参数
  ASSERT validateWeightRange(request.initialWeight, request.targetWeight) = true
  
  // 步骤 5: 冻结参与者赌金
  freezeResult ← freezeFunds(userId, plan.id, plan.betAmount)
  IF freezeResult.success = false THEN
    THROW PaymentError("资金冻结失败")
  END IF
  
  // 步骤 6: 更新计划
  plan.participantId ← userId
  plan.status ← PlanStatus.active
  plan.activatedAt ← now()
  plan.participantGoal ← {
    initialWeight: request.initialWeight,
    targetWeight: request.targetWeight,
    targetWeightLoss: request.initialWeight - request.targetWeight
  }
  
  // 步骤 7: 保存更新
  updatedPlan ← database.update(plan)
  
  // 步骤 8: 发送通知
  sendNotification(plan.creatorId, "计划已生效")
  sendNotification(userId, "计划已生效")
  
  // 后置条件验证
  ASSERT updatedPlan.status = PlanStatus.active
  ASSERT updatedPlan.participantId = userId
  ASSERT updatedPlan.activatedAt ≠ null
  
  RETURN updatedPlan
END
```


### 主算法 3: 执行结算

```dart
Future<Settlement> executeSettlement(String planId) async
```

**前置条件**:
- planId 是有效的计划 ID
- 计划状态为 PlanStatus.active
- 当前时间 >= plan.endDate
- 计划尚未结算过

**后置条件**:
- 返回有效的 Settlement 对象
- 计划状态变为 PlanStatus.completed
- 资金已按规则转移
- 双方收到结算通知
- 结算明细已保存

**循环不变式**: 不适用(无循环)

```pascal
ALGORITHM executeSettlement(planId)
INPUT: planId (String)
OUTPUT: settlement (Settlement)

BEGIN
  // 前置条件验证
  plan ← database.findPlanById(planId)
  ASSERT plan ≠ null
  ASSERT plan.status = PlanStatus.active
  ASSERT now() >= plan.endDate
  
  // 步骤 1: 获取双方最终体重数据
  creatorFinalWeight ← getLatestWeight(plan.creatorId, plan.id)
  participantFinalWeight ← getLatestWeight(plan.participantId, plan.id)
  
  IF creatorFinalWeight = null OR participantFinalWeight = null THEN
    THROW DataError("缺少最终体重数据")
  END IF
  
  // 步骤 2: 计算实际减重量
  creatorWeightLoss ← plan.creatorGoal.initialWeight - creatorFinalWeight
  participantWeightLoss ← plan.participantGoal.initialWeight - participantFinalWeight
  
  // 步骤 3: 判断是否达成目标
  creatorAchieved ← (creatorWeightLoss >= plan.creatorGoal.targetWeightLoss)
  participantAchieved ← (participantWeightLoss >= plan.participantGoal.targetWeightLoss)
  
  // 步骤 4: 应用结算规则
  totalBet ← plan.betAmount * 2
  
  IF creatorAchieved AND participantAchieved THEN
    // 双方都达成: 原路返还,无手续费
    creatorAmount ← plan.betAmount
    participantAmount ← plan.betAmount
    platformFee ← 0
  ELSE IF NOT creatorAchieved AND NOT participantAchieved THEN
    // 双方都未达成: 扣除 10% 手续费后返还
    platformFee ← totalBet * 0.10
    remaining ← totalBet - platformFee
    creatorAmount ← remaining / 2
    participantAmount ← remaining / 2
  ELSE IF creatorAchieved AND NOT participantAchieved THEN
    // 创建者达成,参与者未达成: 创建者获得全部
    creatorAmount ← totalBet
    participantAmount ← 0
    platformFee ← 0
  ELSE
    // 参与者达成,创建者未达成: 参与者获得全部
    creatorAmount ← 0
    participantAmount ← totalBet
    platformFee ← 0
  END IF
  
  // 步骤 5: 创建结算记录
  settlement ← NEW Settlement {
    id: generateUUID(),
    planId: plan.id,
    result: {
      creatorAchieved: creatorAchieved,
      participantAchieved: participantAchieved,
      creatorFinalWeight: creatorFinalWeight,
      participantFinalWeight: participantFinalWeight,
      creatorWeightLoss: creatorWeightLoss,
      participantWeightLoss: participantWeightLoss
    },
    creatorAmount: creatorAmount,
    participantAmount: participantAmount,
    platformFee: platformFee,
    settlementDate: now()
  }
  
  // 步骤 6: 执行资金转移
  unfreezeFunds(plan.creatorId, plan.id)
  unfreezeFunds(plan.participantId, plan.id)
  
  IF creatorAmount > 0 THEN
    transferFunds("platform", plan.creatorId, creatorAmount)
  END IF
  
  IF participantAmount > 0 THEN
    transferFunds("platform", plan.participantId, participantAmount)
  END IF
  
  // 步骤 7: 更新计划状态
  plan.status ← PlanStatus.completed
  database.update(plan)
  
  // 步骤 8: 保存结算记录
  savedSettlement ← database.save(settlement)
  
  // 步骤 9: 发送通知
  sendSettlementNotification(plan.creatorId, settlement)
  sendSettlementNotification(plan.participantId, settlement)
  
  // 后置条件验证
  ASSERT savedSettlement.creatorAmount + savedSettlement.participantAmount + savedSettlement.platformFee = totalBet
  ASSERT plan.status = PlanStatus.completed
  
  RETURN savedSettlement
END
```


### 辅助算法 1: 验证打卡数据

```dart
Future<ValidationResult> validateCheckInData(CheckInData data) async
```

**前置条件**:
- data 包含必要的字段(userId, planId, weight, checkInDate)
- weight 在合理范围内(30-300 kg)

**后置条件**:
- 返回 ValidationResult 对象,包含验证结果和原因
- 如果验证通过,result.isValid = true
- 如果验证失败,result.reason 包含失败原因

**循环不变式**: 不适用(无循环)

```pascal
ALGORITHM validateCheckInData(data)
INPUT: data (CheckInData)
OUTPUT: result (ValidationResult)

BEGIN
  // 步骤 1: 基本数据验证
  IF data.weight < 30 OR data.weight > 300 THEN
    RETURN ValidationResult(false, "体重数据超出合理范围")
  END IF
  
  // 步骤 2: 获取计划信息
  plan ← database.findPlanById(data.planId)
  IF plan = null THEN
    RETURN ValidationResult(false, "计划不存在")
  END IF
  
  // 步骤 3: 验证打卡日期
  IF data.checkInDate < plan.startDate OR data.checkInDate > plan.endDate THEN
    RETURN ValidationResult(false, "打卡日期不在计划期间内")
  END IF
  
  // 步骤 4: 检查是否重复打卡
  existingCheckIn ← database.findCheckIn(data.userId, data.planId, data.checkInDate)
  IF existingCheckIn ≠ null THEN
    RETURN ValidationResult(false, "今日已打卡")
  END IF
  
  // 步骤 5: 获取用户历史体重数据
  previousCheckIns ← database.getCheckInHistory(data.userId, data.planId)
  
  // 步骤 6: 验证体重变化合理性
  IF previousCheckIns.length > 0 THEN
    lastWeight ← previousCheckIns[previousCheckIns.length - 1].weight
    weightChange ← abs(data.weight - lastWeight)
    daysDiff ← daysBetween(previousCheckIns[previousCheckIns.length - 1].checkInDate, data.checkInDate)
    
    // 每天体重变化不应超过 2kg (异常情况)
    maxChangePerDay ← 2.0
    IF weightChange / daysDiff > maxChangePerDay THEN
      RETURN ValidationResult(false, "体重变化异常,需要人工审核")
    END IF
  END IF
  
  // 步骤 7: 如果提供了照片,进行 AI 验证
  IF data.photoUrl ≠ null THEN
    aiResult ← aiValidateWeightPhoto(data.photoUrl, data.weight)
    IF aiResult.confidence < 0.8 THEN
      RETURN ValidationResult(false, "照片验证失败,需要人工审核")
    END IF
  END IF
  
  // 所有验证通过
  RETURN ValidationResult(true, "验证通过")
END
```


### 辅助算法 2: 计算用户进度

```dart
Future<ProgressStats> calculateProgress(String planId, String userId) async
```

**前置条件**:
- planId 和 userId 是有效的
- 用户是该计划的参与者

**后置条件**:
- 返回包含进度统计的 ProgressStats 对象
- progressPercentage 在 0-100 之间
- 所有统计数据准确反映当前状态

**循环不变式**: 在遍历打卡记录时,已处理的记录数据保持一致性

```pascal
ALGORITHM calculateProgress(planId, userId)
INPUT: planId (String), userId (String)
OUTPUT: stats (ProgressStats)

BEGIN
  // 步骤 1: 获取计划和目标
  plan ← database.findPlanById(planId)
  ASSERT plan ≠ null
  
  IF plan.creatorId = userId THEN
    goal ← plan.creatorGoal
  ELSE IF plan.participantId = userId THEN
    goal ← plan.participantGoal
  ELSE
    THROW PermissionError("用户不是该计划的参与者")
  END IF
  
  // 步骤 2: 获取所有打卡记录
  checkIns ← database.getCheckInHistory(planId, userId)
  
  IF checkIns.length = 0 THEN
    RETURN ProgressStats {
      currentWeight: goal.initialWeight,
      initialWeight: goal.initialWeight,
      targetWeight: goal.targetWeight,
      weightLoss: 0,
      targetWeightLoss: goal.targetWeightLoss,
      progressPercentage: 0,
      checkInCount: 0,
      daysRemaining: daysBetween(now(), plan.endDate)
    }
  END IF
  
  // 步骤 3: 获取最新体重
  latestCheckIn ← checkIns[checkIns.length - 1]
  currentWeight ← latestCheckIn.weight
  
  // 步骤 4: 计算减重量和进度
  weightLoss ← goal.initialWeight - currentWeight
  progressPercentage ← (weightLoss / goal.targetWeightLoss) * 100
  
  // 确保进度百分比在合理范围内
  IF progressPercentage < 0 THEN
    progressPercentage ← 0
  END IF
  IF progressPercentage > 100 THEN
    progressPercentage ← 100
  END IF
  
  // 步骤 5: 计算剩余天数
  daysRemaining ← daysBetween(now(), plan.endDate)
  IF daysRemaining < 0 THEN
    daysRemaining ← 0
  END IF
  
  // 步骤 6: 构建统计对象
  stats ← ProgressStats {
    currentWeight: currentWeight,
    initialWeight: goal.initialWeight,
    targetWeight: goal.targetWeight,
    weightLoss: weightLoss,
    targetWeightLoss: goal.targetWeightLoss,
    progressPercentage: progressPercentage,
    checkInCount: checkIns.length,
    daysRemaining: daysRemaining
  }
  
  // 后置条件验证
  ASSERT stats.progressPercentage >= 0 AND stats.progressPercentage <= 100
  
  RETURN stats
END
```

## 关键函数的形式化规范

### 函数 1: freezeFunds()

```dart
Future<FreezeResult> freezeFunds(String userId, String planId, double amount)
```

**前置条件**:
- userId 是有效的已注册用户
- planId 是有效的计划 ID
- amount > 0
- 用户账户余额 >= amount

**后置条件**:
- 如果成功: result.success = true,用户可用余额减少 amount,冻结余额增加 amount
- 如果失败: result.success = false,result.error 包含错误信息,账户余额不变
- 创建一条 TransactionType.freeze 的交易记录

**循环不变式**: 不适用(无循环)

### 函数 2: unfreezeFunds()

```dart
Future<void> unfreezeFunds(String userId, String planId)
```

**前置条件**:
- userId 是有效的已注册用户
- planId 是有效的计划 ID
- 存在与该 planId 关联的冻结资金

**后置条件**:
- 用户冻结余额减少相应金额
- 用户可用余额增加相应金额
- 创建一条 TransactionType.unfreeze 的交易记录

**循环不变式**: 不适用(无循环)


### 函数 3: transferFunds()

```dart
Future<TransferResult> transferFunds(String fromUserId, String toUserId, double amount)
```

**前置条件**:
- fromUserId 和 toUserId 是有效的用户 ID
- amount > 0
- fromUserId 的可用余额 >= amount

**后置条件**:
- fromUserId 的可用余额减少 amount
- toUserId 的可用余额增加 amount
- 创建两条交易记录(一条扣款,一条入账)
- 如果转账失败,双方余额保持不变

**循环不变式**: 不适用(无循环)

### 函数 4: getLatestWeight()

```dart
Future<double?> getLatestWeight(String userId, String planId)
```

**前置条件**:
- userId 和 planId 是有效的
- 用户是该计划的参与者

**后置条件**:
- 如果存在打卡记录,返回最新的体重值
- 如果不存在打卡记录,返回 null
- 返回的体重值在合理范围内(30-300 kg)

**循环不变式**: 不适用(无循环)

## 示例用法

### 示例 1: 创建对赌计划

```dart
// 用户 A 创建减肥计划
final request = CreatePlanRequest(
  betAmount: 100.0,
  startDate: DateTime.now(),
  endDate: DateTime.now().add(Duration(days: 30)),
  initialWeight: 80.0,
  targetWeight: 75.0,
  description: "30天减重5kg挑战",
  inviteeId: "user_b_id",
);

try {
  final plan = await bettingPlanService.createPlan("user_a_id", request);
  print("计划创建成功: ${plan.id}");
  print("状态: ${plan.status}"); // PlanStatus.pending
} catch (e) {
  print("创建失败: $e");
}
```

### 示例 2: 接受对赌计划

```dart
// 用户 B 接受计划
final acceptRequest = AcceptPlanRequest(
  initialWeight: 85.0,
  targetWeight: 78.0,
);

try {
  final plan = await bettingPlanService.acceptPlan(
    "plan_id",
    "user_b_id",
    acceptRequest,
  );
  print("计划已生效: ${plan.status}"); // PlanStatus.active
  print("开始日期: ${plan.activatedAt}");
} catch (e) {
  print("接受失败: $e");
}
```

### 示例 3: 每日打卡

```dart
// 用户每日打卡
final checkInData = CheckInData(
  userId: "user_a_id",
  planId: "plan_id",
  weight: 78.5,
  checkInDate: DateTime.now(),
  photoUrl: "https://example.com/weight-photo.jpg",
  note: "今天感觉很好!",
);

try {
  // 验证数据
  final validation = await checkInService.validateCheckInData(checkInData);
  if (!validation.isValid) {
    print("验证失败: ${validation.reason}");
    return;
  }
  
  // 创建打卡记录
  final checkIn = await checkInService.createCheckIn(
    checkInData.userId,
    checkInData.planId,
    checkInData,
  );
  print("打卡成功: ${checkIn.id}");
  
  // 获取进度
  final progress = await checkInService.getProgress("plan_id", "user_a_id");
  print("当前进度: ${progress.progressPercentage}%");
  print("已减重: ${progress.weightLoss} kg");
} catch (e) {
  print("打卡失败: $e");
}
```

### 示例 4: 完整工作流程

```dart
// 完整的对赌流程
Future<void> completeBettingWorkflow() async {
  // 1. 用户 A 创建计划
  final createRequest = CreatePlanRequest(
    betAmount: 100.0,
    startDate: DateTime.now(),
    endDate: DateTime.now().add(Duration(days: 30)),
    initialWeight: 80.0,
    targetWeight: 75.0,
    description: "30天减重5kg挑战",
  );
  
  final plan = await bettingPlanService.createPlan("user_a_id", createRequest);
  
  // 2. 邀请用户 B
  await bettingPlanService.inviteParticipant(plan.id, "user_b_id");
  
  // 3. 用户 B 接受计划
  final acceptRequest = AcceptPlanRequest(
    initialWeight: 85.0,
    targetWeight: 78.0,
  );
  
  final activePlan = await bettingPlanService.acceptPlan(
    plan.id,
    "user_b_id",
    acceptRequest,
  );
  
  // 4. 双方每日打卡 (模拟)
  for (int day = 0; day < 30; day++) {
    // 用户 A 打卡
    await checkInService.createCheckIn(
      "user_a_id",
      activePlan.id,
      CheckInData(
        userId: "user_a_id",
        planId: activePlan.id,
        weight: 80.0 - (day * 0.2), // 模拟逐渐减重
        checkInDate: DateTime.now().add(Duration(days: day)),
      ),
    );
    
    // 用户 B 打卡
    await checkInService.createCheckIn(
      "user_b_id",
      activePlan.id,
      CheckInData(
        userId: "user_b_id",
        planId: activePlan.id,
        weight: 85.0 - (day * 0.25), // 模拟逐渐减重
        checkInDate: DateTime.now().add(Duration(days: day)),
      ),
    );
  }
  
  // 5. 计划到期,自动结算
  final settlement = await settlementService.executeSettlement(activePlan.id);
  
  print("结算完成:");
  print("用户 A 达成目标: ${settlement.result.creatorAchieved}");
  print("用户 B 达成目标: ${settlement.result.participantAchieved}");
  print("用户 A 获得金额: ${settlement.creatorAmount}");
  print("用户 B 获得金额: ${settlement.participantAmount}");
  print("平台手续费: ${settlement.platformFee}");
}
```


## 正确性属性

### 属性 1: 资金守恒

**描述**: 在任何时刻,系统中的总资金(用户余额 + 冻结资金 + 平台收入)必须等于所有充值金额减去所有提现金额。

**形式化表达**:
```
∀t ∈ Time: 
  Σ(user.balance) + Σ(user.frozenBalance) + platformRevenue = 
  Σ(deposits) - Σ(withdrawals)
```

**验证方法**: 在每次资金操作后进行审计检查

### 属性 2: 结算规则正确性

**描述**: 结算金额分配必须严格遵循规则,且总和等于双方赌金之和。

**形式化表达**:
```
∀settlement ∈ Settlements:
  settlement.creatorAmount + settlement.participantAmount + settlement.platformFee = 
  2 * settlement.plan.betAmount
  
  AND
  
  (creatorAchieved ∧ participantAchieved) ⟹ 
    (creatorAmount = betAmount ∧ participantAmount = betAmount ∧ platformFee = 0)
  
  (¬creatorAchieved ∧ ¬participantAchieved) ⟹ 
    (platformFee = totalBet * 0.10 ∧ creatorAmount = participantAmount)
  
  (creatorAchieved ∧ ¬participantAchieved) ⟹ 
    (creatorAmount = totalBet ∧ participantAmount = 0 ∧ platformFee = 0)
  
  (¬creatorAchieved ∧ participantAchieved) ⟹ 
    (creatorAmount = 0 ∧ participantAmount = totalBet ∧ platformFee = 0)
```

### 属性 3: 计划状态转换合法性

**描述**: 计划状态只能按照规定的顺序转换。

**形式化表达**:
```
∀plan ∈ BettingPlans:
  (plan.status = pending) ⟹ 
    next(plan.status) ∈ {active, cancelled, rejected}
  
  (plan.status = active) ⟹ 
    next(plan.status) = completed
  
  (plan.status ∈ {completed, cancelled, rejected}) ⟹ 
    next(plan.status) = plan.status  // 终态,不再改变
```

### 属性 4: 打卡唯一性

**描述**: 每个用户在每个计划中每天只能打卡一次。

**形式化表达**:
```
∀checkIn1, checkIn2 ∈ CheckIns:
  (checkIn1.userId = checkIn2.userId ∧ 
   checkIn1.planId = checkIn2.planId ∧ 
   sameDay(checkIn1.checkInDate, checkIn2.checkInDate)) ⟹ 
  checkIn1.id = checkIn2.id
```

### 属性 5: 体重数据合理性

**描述**: 体重数据必须在合理范围内,且相邻打卡的体重变化不应过大。

**形式化表达**:
```
∀checkIn ∈ CheckIns:
  30 ≤ checkIn.weight ≤ 300
  
  AND
  
∀checkIn1, checkIn2 ∈ CheckIns:
  (checkIn1.userId = checkIn2.userId ∧ 
   checkIn1.planId = checkIn2.planId ∧ 
   checkIn2.checkInDate = checkIn1.checkInDate + 1day) ⟹ 
  |checkIn2.weight - checkIn1.weight| ≤ 2.0
```

### 属性 6: 结算时机正确性

**描述**: 结算只能在计划到期后执行,且每个计划只能结算一次。

**形式化表达**:
```
∀settlement ∈ Settlements:
  settlement.settlementDate ≥ settlement.plan.endDate
  
  AND
  
∀plan ∈ BettingPlans:
  |{s ∈ Settlements : s.planId = plan.id}| ≤ 1
```

### 属性 7: 权限控制

**描述**: 用户只能操作自己参与的计划。

**形式化表达**:
```
∀operation ∈ {createCheckIn, getProgress, acceptPlan}:
  operation(userId, planId) ⟹ 
  (plan.creatorId = userId ∨ plan.participantId = userId)
```

## 错误处理

### 错误场景 1: 余额不足

**条件**: 用户尝试创建或接受计划时,账户余额小于赌金金额

**响应**: 
- 返回 InsufficientBalanceError
- 提示用户充值
- 不创建计划或不冻结资金

**恢复**: 用户充值后可重新尝试

### 错误场景 2: 支付网关失败

**条件**: 与第三方支付网关通信失败或支付处理失败

**响应**:
- 返回 PaymentGatewayError
- 记录错误日志
- 不改变用户余额
- 如果是冻结资金失败,不创建或激活计划

**恢复**: 
- 自动重试(最多3次)
- 如果持续失败,通知用户稍后重试
- 如果是计划创建过程中失败,回滚已创建的计划

### 错误场景 3: 重复打卡

**条件**: 用户在同一天内尝试多次打卡

**响应**:
- 返回 DuplicateCheckInError
- 提示用户今日已打卡
- 不创建新的打卡记录

**恢复**: 用户可以在第二天再次打卡


### 错误场景 4: 体重数据异常

**条件**: 打卡时提交的体重数据与历史数据相比变化过大

**响应**:
- 返回 AbnormalWeightChangeError
- 将打卡记录标记为需要人工审核
- 通知对方和平台管理员
- 暂时接受打卡,但标记为 ReviewStatus.pending

**恢复**: 
- 等待人工审核
- 如果审核通过,状态变为 approved
- 如果审核拒绝,状态变为 rejected,该打卡不计入结算

### 错误场景 5: 计划到期无打卡数据

**条件**: 计划到期时,一方或双方没有任何打卡记录

**响应**:
- 无法获取最终体重,抛出 DataError
- 将该方视为未达成目标
- 按照"未达成目标"规则进行结算
- 记录异常情况到日志

**恢复**: 
- 自动按规则结算
- 如果双方都无数据,按"双方未达成"处理
- 发送通知提醒用户打卡的重要性

### 错误场景 6: 结算争议

**条件**: 用户对结算结果提出异议

**响应**:
- 创建争议记录
- 暂停资金转移(如果尚未完成)
- 通知平台管理员
- 提供争议处理流程

**恢复**:
- 人工审核争议
- 如果争议成立,重新计算结算
- 如果争议不成立,维持原结算结果
- 完成资金转移

### 错误场景 7: 网络超时

**条件**: 客户端与服务器通信超时

**响应**:
- 返回 NetworkTimeoutError
- 不改变服务器状态
- 提示用户检查网络连接

**恢复**:
- 客户端自动重试(指数退避)
- 用户可手动刷新
- 对于关键操作(如支付),使用幂等性保证不重复执行

## 测试策略

### 单元测试方法

**目标**: 测试各个组件和函数的独立功能

**关键测试用例**:

1. **认证服务测试**
   - 测试有效凭证登录成功
   - 测试无效凭证登录失败
   - 测试令牌生成和验证
   - 测试第三方登录集成

2. **对赌计划服务测试**
   - 测试创建计划的参数验证
   - 测试计划状态转换
   - 测试邀请和接受流程
   - 测试取消和拒绝逻辑

3. **打卡服务测试**
   - 测试打卡数据验证
   - 测试重复打卡检测
   - 测试进度计算准确性
   - 测试异常数据处理

4. **支付服务测试**
   - 测试资金冻结和解冻
   - 测试余额不足处理
   - 测试转账逻辑
   - 测试交易记录生成

5. **结算服务测试**
   - 测试四种结算场景(双方达成、双方未达成、一方达成)
   - 测试结算金额计算
   - 测试手续费计算
   - 测试结算时机控制

**覆盖率目标**: 代码覆盖率 > 80%,关键路径覆盖率 100%

### 基于属性的测试方法

**目标**: 验证系统的不变性和正确性属性

**属性测试库**: 使用 Dart 的 `test` 包配合自定义属性测试框架

**关键属性测试**:

1. **资金守恒属性测试**
   ```dart
   property("资金总量守恒", () {
     // 生成随机的资金操作序列
     final operations = generateRandomOperations();
     
     // 执行操作
     final initialTotal = calculateTotalFunds();
     executeOperations(operations);
     final finalTotal = calculateTotalFunds();
     
     // 验证总量不变(除了充值和提现)
     expect(finalTotal, equals(initialTotal + deposits - withdrawals));
   });
   ```

2. **结算规则属性测试**
   ```dart
   property("结算金额总和等于双倍赌金", () {
     // 生成随机的计划和结果
     final plan = generateRandomPlan();
     final creatorAchieved = randomBool();
     final participantAchieved = randomBool();
     
     // 执行结算
     final settlement = calculateSettlement(plan, creatorAchieved, participantAchieved);
     
     // 验证总和
     expect(
       settlement.creatorAmount + settlement.participantAmount + settlement.platformFee,
       equals(2 * plan.betAmount),
     );
   });
   ```

3. **状态转换属性测试**
   ```dart
   property("计划状态转换合法", () {
     // 生成随机的状态转换序列
     final plan = createPlan();
     final transitions = generateRandomTransitions();
     
     // 验证每次转换都合法
     for (final transition in transitions) {
       final isValid = isValidTransition(plan.status, transition);
       if (isValid) {
         plan.status = transition;
       }
     }
     
     // 验证最终状态合法
     expect(isValidFinalState(plan.status), isTrue);
   });
   ```

4. **体重数据合理性属性测试**
   ```dart
   property("体重变化在合理范围内", () {
     // 生成随机的打卡序列
     final checkIns = generateRandomCheckIns();
     
     // 验证每次变化都合理
     for (int i = 1; i < checkIns.length; i++) {
       final change = (checkIns[i].weight - checkIns[i-1].weight).abs();
       final daysDiff = checkIns[i].checkInDate.difference(checkIns[i-1].checkInDate).inDays;
       
       expect(change / daysDiff, lessThanOrEqualTo(2.0));
     }
   });
   ```


### 集成测试方法

**目标**: 测试多个组件协同工作的场景

**关键集成测试场景**:

1. **完整对赌流程测试**
   - 用户 A 创建计划 → 邀请用户 B → 用户 B 接受 → 双方打卡 → 自动结算
   - 验证每个步骤的状态变化
   - 验证资金流转正确性
   - 验证通知发送

2. **支付集成测试**
   - 测试与第三方支付网关的集成
   - 测试支付成功和失败场景
   - 测试支付回调处理
   - 测试支付安全性

3. **定时任务测试**
   - 测试结算定时任务触发
   - 测试打卡提醒定时任务
   - 测试任务失败重试机制

4. **并发场景测试**
   - 测试多个用户同时创建计划
   - 测试同一计划的并发打卡
   - 测试并发结算请求
   - 验证数据一致性

5. **端到端测试**
   - 使用真实的 Flutter 客户端
   - 测试完整的用户旅程
   - 测试 UI 交互和数据同步
   - 测试离线场景和数据恢复

**测试环境**: 使用独立的测试数据库和模拟的支付网关

## 性能考虑

### 性能需求

1. **响应时间**
   - API 响应时间 < 200ms (P95)
   - 打卡操作 < 500ms
   - 结算计算 < 1s

2. **并发能力**
   - 支持 10,000+ 并发用户
   - 支持 1,000+ 并发打卡请求
   - 支持 100+ 并发结算任务

3. **数据库性能**
   - 查询响应时间 < 100ms
   - 支持 100,000+ 活跃计划
   - 支持 1,000,000+ 打卡记录

### 优化策略

1. **数据库优化**
   - 为常用查询字段添加索引(userId, planId, checkInDate)
   - 使用数据库连接池
   - 对历史数据进行分区存储
   - 使用读写分离架构

2. **缓存策略**
   - 使用 Redis 缓存用户信息和计划详情
   - 缓存排行榜数据(TTL: 5分钟)
   - 缓存用户余额信息(TTL: 1分钟)
   - 使用 CDN 缓存静态资源

3. **异步处理**
   - 使用消息队列处理通知发送
   - 异步处理图片上传和 AI 验证
   - 异步生成统计报表
   - 使用后台任务处理结算

4. **API 优化**
   - 使用分页减少数据传输量
   - 实现 GraphQL 支持按需查询
   - 使用 gRPC 提升内部服务通信效率
   - 实现 API 响应压缩

5. **移动端优化**
   - 实现本地数据缓存
   - 使用增量同步减少数据传输
   - 实现图片压缩和懒加载
   - 优化 Flutter 渲染性能

### 监控指标

- API 响应时间分布
- 数据库查询性能
- 缓存命中率
- 错误率和失败率
- 用户活跃度和留存率
- 支付成功率

## 安全考虑

### 安全需求

1. **身份认证和授权**
   - 使用 JWT 令牌进行身份验证
   - 实现基于角色的访问控制(RBAC)
   - 支持多因素认证(MFA)
   - 实现会话管理和令牌刷新

2. **数据加密**
   - 使用 HTTPS/TLS 加密所有网络通信
   - 敏感数据(密码、支付信息)使用 AES-256 加密存储
   - 使用 bcrypt 或 Argon2 哈希密码
   - 加密数据库备份

3. **支付安全**
   - 遵循 PCI DSS 标准
   - 不存储完整的信用卡信息
   - 使用支付令牌化
   - 实现交易签名验证
   - 支持 3D Secure 验证

4. **API 安全**
   - 实现请求限流(Rate Limiting)
   - 防止 SQL 注入和 XSS 攻击
   - 验证所有输入参数
   - 实现 CSRF 保护
   - 使用 API 密钥和签名

5. **数据隐私**
   - 遵循 GDPR 和相关隐私法规
   - 实现数据最小化原则
   - 提供用户数据导出和删除功能
   - 匿名化统计数据
   - 定期进行安全审计

### 威胁模型

1. **账户劫持**
   - 威胁: 攻击者获取用户凭证
   - 缓解: 强密码策略、MFA、异常登录检测

2. **支付欺诈**
   - 威胁: 虚假打卡数据、恶意结算
   - 缓解: AI 验证、人工审核、风控系统

3. **数据泄露**
   - 威胁: 敏感数据被窃取
   - 缓解: 加密存储、访问控制、安全审计

4. **DDoS 攻击**
   - 威胁: 服务不可用
   - 缓解: CDN、限流、负载均衡

5. **内部威胁**
   - 威胁: 内部人员滥用权限
   - 缓解: 最小权限原则、操作日志、定期审计

### 安全最佳实践

- 定期更新依赖库和框架
- 进行定期的安全测试和渗透测试
- 实现完善的日志记录和监控
- 建立安全事件响应流程
- 对开发人员进行安全培训


## 依赖项

### 移动端依赖 (Flutter/Dart)

**核心框架**:
- `flutter`: ^3.0.0 - Flutter SDK
- `dart`: ^3.0.0 - Dart 语言

**状态管理**:
- `provider`: ^6.0.0 或 `riverpod`: ^2.0.0 - 状态管理
- `flutter_bloc`: ^8.0.0 - BLoC 模式(可选)

**网络请求**:
- `dio`: ^5.0.0 - HTTP 客户端
- `retrofit`: ^4.0.0 - 类型安全的 HTTP 客户端
- `json_serializable`: ^6.0.0 - JSON 序列化

**本地存储**:
- `shared_preferences`: ^2.0.0 - 键值存储
- `sqflite`: ^2.0.0 - SQLite 数据库
- `hive`: ^2.0.0 - 轻量级 NoSQL 数据库

**认证**:
- `firebase_auth`: ^4.0.0 - Firebase 认证
- `google_sign_in`: ^6.0.0 - Google 登录
- `flutter_secure_storage`: ^8.0.0 - 安全存储

**支付**:
- `stripe_flutter`: ^9.0.0 - Stripe 支付集成
- `in_app_purchase`: ^3.0.0 - 应用内购买

**UI 组件**:
- `flutter_svg`: ^2.0.0 - SVG 支持
- `cached_network_image`: ^3.0.0 - 图片缓存
- `fl_chart`: ^0.60.0 - 图表库
- `shimmer`: ^3.0.0 - 加载动画

**工具库**:
- `intl`: ^0.18.0 - 国际化
- `timeago`: ^3.0.0 - 时间格式化
- `image_picker`: ^1.0.0 - 图片选择
- `permission_handler`: ^11.0.0 - 权限管理

**测试**:
- `flutter_test`: SDK - Flutter 测试框架
- `mockito`: ^5.0.0 - Mock 框架
- `integration_test`: SDK - 集成测试

### 后端依赖

**推荐技术栈选项 1: Node.js + TypeScript**

- `express`: ^4.18.0 - Web 框架
- `typescript`: ^5.0.0 - TypeScript
- `typeorm`: ^0.3.0 - ORM
- `jsonwebtoken`: ^9.0.0 - JWT 认证
- `bcrypt`: ^5.0.0 - 密码哈希
- `stripe`: ^12.0.0 - Stripe SDK
- `node-cron`: ^3.0.0 - 定时任务
- `redis`: ^4.0.0 - Redis 客户端
- `winston`: ^3.0.0 - 日志库
- `joi`: ^17.0.0 - 数据验证

**推荐技术栈选项 2: Python + FastAPI**

- `fastapi`: ^0.100.0 - Web 框架
- `sqlalchemy`: ^2.0.0 - ORM
- `pydantic`: ^2.0.0 - 数据验证
- `pyjwt`: ^2.0.0 - JWT 认证
- `bcrypt`: ^4.0.0 - 密码哈希
- `stripe`: ^5.0.0 - Stripe SDK
- `celery`: ^5.0.0 - 异步任务
- `redis`: ^4.0.0 - Redis 客户端
- `pytest`: ^7.0.0 - 测试框架

**推荐技术栈选项 3: Java + Spring Boot**

- `spring-boot`: ^3.0.0 - Spring Boot 框架
- `spring-security`: ^6.0.0 - 安全框架
- `spring-data-jpa`: ^3.0.0 - JPA
- `jjwt`: ^0.11.0 - JWT 库
- `stripe-java`: ^22.0.0 - Stripe SDK
- `quartz`: ^2.3.0 - 定时任务
- `jedis`: ^4.0.0 - Redis 客户端
- `junit`: ^5.0.0 - 测试框架

### 数据库

**主数据库**:
- PostgreSQL 14+ 或 MySQL 8+ - 关系型数据库
- 用于存储用户、计划、打卡、交易等核心数据

**缓存数据库**:
- Redis 7+ - 内存数据库
- 用于缓存、会话管理、排行榜

**文件存储**:
- AWS S3 或 Google Cloud Storage - 对象存储
- 用于存储用户上传的图片

### 第三方服务

**支付网关**:
- Stripe - 国际支付
- PayPal - 备选支付方式

**认证服务**:
- Firebase Authentication - 第三方登录
- Auth0 - 备选认证服务

**推送通知**:
- Firebase Cloud Messaging (FCM) - Android 推送
- Apple Push Notification Service (APNs) - iOS 推送

**监控和分析**:
- Sentry - 错误追踪
- Google Analytics - 用户分析
- Mixpanel - 事件分析

**AI 服务**:
- Google Cloud Vision API - 图片识别
- AWS Rekognition - 备选图片识别

### 开发工具

**版本控制**:
- Git - 版本控制
- GitHub/GitLab - 代码托管

**CI/CD**:
- GitHub Actions 或 GitLab CI - 持续集成
- Fastlane - 移动端自动化部署

**API 文档**:
- Swagger/OpenAPI - API 文档生成
- Postman - API 测试

**项目管理**:
- Jira 或 Linear - 任务管理
- Confluence - 文档管理

## 实现路线图

### 阶段 1: MVP (最小可行产品) - 4-6 周

**目标**: 实现核心对赌功能

**功能范围**:
- 用户注册和登录(邮箱/手机号)
- 创建和接受对赌计划
- 每日打卡(手动输入体重)
- 自动结算
- 基础的用户界面

**技术实现**:
- Flutter 移动端(Android 优先)
- 后端 API(选择一个技术栈)
- PostgreSQL 数据库
- 基础的支付集成(测试模式)

### 阶段 2: 增强功能 - 4-6 周

**目标**: 完善核心功能和用户体验

**功能范围**:
- 第三方登录(Google)
- 照片上传和验证
- 进度图表和统计
- 打卡提醒通知
- iOS 版本开发
- 支付集成(生产模式)

**技术实现**:
- Firebase Authentication
- 图片存储(S3)
- 推送通知(FCM/APNs)
- 图表库集成

### 阶段 3: 社交功能 - 3-4 周

**目标**: 增加社交互动和用户粘性

**功能范围**:
- 排行榜
- 评论和鼓励
- 勋章系统
- 用户主页
- 好友系统

**技术实现**:
- 社交数据模型
- 实时更新(WebSocket 或轮询)
- 成就系统

### 阶段 4: 高级功能 - 4-6 周

**目标**: 提供更多玩法和优化

**功能范围**:
- 多人群组挑战
- AI 图片验证
- 数据分析和洞察
- 个性化推荐
- 提现功能

**技术实现**:
- 群组数据模型
- AI 服务集成
- 数据分析管道
- 推荐算法

### 阶段 5: 优化和扩展 - 持续

**目标**: 性能优化和功能扩展

**功能范围**:
- 性能优化
- 安全加固
- 多语言支持
- 更多支付方式
- 运营工具

**技术实现**:
- 缓存优化
- 数据库优化
- 安全审计
- 国际化
- 管理后台
