# 减肥对赌 APP - Weight Loss Betting App

一个基于对赌机制的减肥激励应用，通过金钱激励和社交监督帮助用户达成减肥目标。

## 项目概述

本项目是一个完整的三端应用（后端 API + Android 客户端 + iOS 客户端），用户可以：
- 创建减肥挑战并设置赌金
- 邀请好友参与对赌
- 每日打卡记录体重变化
- 根据目标达成情况进行结算
- 查看排行榜和社交互动

## 技术架构

### 后端 (Backend)
- **框架**: FastAPI 0.104+ (Python 3.14)
- **数据库**: PostgreSQL 14+ / SQLite (开发环境)
- **ORM**: SQLAlchemy 2.0+ + Alembic (迁移管理)
- **缓存**: Redis 7+
- **支付**: Stripe SDK 7.7+
- **认证**: JWT (python-jose) + bcrypt 哈希
- **通知**: Firebase Cloud Messaging + APNs
- **日志**: Loguru
- **中间件**: 
  - 限流中间件（100 req/min）
  - CORS 跨域支持
  - GZip 压缩
  - 安全中间件（XSS/CSRF 防护）
  - 统一错误处理

### Android 客户端
- **语言**: Kotlin
- **架构**: MVVM + Repository 模式
- **网络**: Retrofit + OkHttp
- **本地存储**: Room Database
- **依赖注入**: Hilt
- **推送**: Firebase Cloud Messaging
- **支付**: Stripe SDK

### iOS 客户端
- **语言**: Swift
- **最低版本**: iOS 14.0
- **网络**: Alamofire
- **本地存储**: Core Data
- **推送**: Apple Push Notification Service
- **支付**: Stripe PaymentSheet

## 核心功能

### 1. 用户认证
- ✅ 邮箱/密码注册登录
- ✅ Google OAuth 第三方登录
- ✅ JWT Token 认证和自动刷新

### 2. 对赌计划
- ✅ 创建减肥对赌计划（设置赌金、时长、目标体重）
- ✅ 自动冻结资金（创建计划时）
- ✅ 邮箱搜索好友并邀请（每个计划限一次邀请）
- ✅ 待接受状态管理（pending → active）
- ✅ 计划状态完整流转（pending → waiting_double_check → active → completed/expired/cancelled/rejected）
- ✅ 资金冻结和解冻机制
- ✅ 放弃待接受计划（原路返还赌金）
- ✅ 放弃进行中计划（判负，资金转给对方）

### 3. 打卡签到
- ✅ 每日体重打卡记录
- ✅ 打卡历史查询
- ✅ 进度统计


### 4. 支付与资金管理
- ✅ Stripe 支付集成
- ✅ 余额查询和交易历史
- ✅ 资金冻结/解冻机制
- ✅ 充值和提现功能
- ✅ PCI DSS 合规


### 5. 结算系统
- ✅ App 检查触发机制（计划到期检查）
- ✅ 三次选择匹配机制：
  - 双方都达成 → 原路返还（无手续费）
  - 双方都未达成 → 扣除 10% 手续费后平分
  - 一方达成 → 获得全部赌金
  - 选择不匹配 → 最多 3 轮后进入仲裁
- ✅ 超时处理（24 小时倒计时）
- ✅ 强制仲裁（扣 15% 费用）
- ✅ 数据库事务保证原子性

### 6. 邀请与放弃计划
- ✅ 好友邀请（通过邮箱搜索，每个计划限一次）
- ✅ 待接受计划放弃（原路返还赌金）
- ✅ 进行中计划放弃（判负，资金转给对方）
- ✅ 邀请限制验证（不能邀请自己，每个计划只能邀请一次）

### 7. 通知系统
- ✅ Firebase Cloud Messaging (Android)
- ✅ Apple Push Notification Service (iOS)
- ✅ 通知场景：邀请通知、计划生效、结算完成、打卡提醒




### 10. 安全与中间件
- ✅ JWT Token 认证和自动刷新
- ✅ 限流中间件（100 req/min）
- ✅ CORS 跨域支持
- ✅ GZip 压缩
- ✅ 统一错误处理
- ✅ SQL 注入防护
- ✅ XSS 和 CSRF 防护

```
tracker/
├── backend/                    # 后端 API
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── api/               # API 路由
│   │   ├── services/          # 业务逻辑
│   │   ├── middleware/        # 中间件
│   │   └── main.py            # 应用入口
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   └── requirements.txt       # Python 依赖
│
├── android/                   # Android 客户端
│   ├── app/
│   │   └── src/main/
│   │       ├── java/com/weightloss/betting/
│   │       │   ├── data/      # 数据层
│   │       │   ├── ui/        # UI 层
│   │       │   └── di/        # 依赖注入
│   │       └── res/           # 资源文件
│   └── build.gradle
│
├── ios/                       # iOS 客户端
│   ├── WeightLossBetting/
│   │   ├── Data/              # 数据层
│   │   ├── UI/                # UI 层
│   │   └── AppDelegate.swift  # 应用入口
│   └── Podfile                # CocoaPods 依赖
│
└── README.md                  # 本文件
```

## 快速开始

### 后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件填写配置

# 初始化数据库
python init_db.py

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/api/docs 查看 API 文档

### Android 客户端

1. 使用 Android Studio 打开 `android/` 目录
2. 同步 Gradle 依赖
3. 配置 API 地址（`NetworkModule.kt` 中的 `BASE_URL`）
4. 运行应用到设备或模拟器

### iOS 客户端

```bash
cd ios

# 安装 CocoaPods 依赖
pod install

# 打开工作空间
open WeightLossBetting.xcworkspace

# 在 Xcode 中配置 API 地址并运行
```

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/google` - Google OAuth 登录
- `POST /api/auth/refresh` - 刷新访问令牌

### 用户
- `GET /api/users/{userId}` - 获取用户信息
- `PUT /api/users/{userId}` - 更新用户信息
- `GET /api/users/{userId}/balance` - 获取账户余额
- `GET /api/users/{userId}/transactions` - 获取交易历史
- `POST /api/users/{userId}/payment-methods` - 绑定支付方式

### 对赌计划
- `POST /api/betting-plans` - 创建对赌计划（自动冻结资金）
- `GET /api/betting-plans/{planId}` - 获取计划详情
- `GET /api/betting-plans` - 获取我的计划列表
- `POST /api/betting-plans/{planId}/accept` - 接受对赌计划
- `POST /api/betting-plans/{planId}/reject` - 拒绝对赌计划
- `POST /api/betting-plans/{planId}/cancel` - 取消对赌计划
- `POST /api/betting-plans/{planId}/abandon` - 放弃计划

### 邀请
- `GET /api/invitations` - 获取邀请列表
- `POST /api/betting-plans/{planId}/invite` - 发送邀请
- `POST /api/invitations/{invitationId}/accept` - 接受邀请
- `POST /api/invitations/{invitationId}/reject` - 拒绝邀请
- `GET /api/friend-search` - 搜索好友（按邮箱）

### 打卡
- `POST /api/check-ins` - 创建打卡记录（上传体重）
- `GET /api/betting-plans/{planId}/check-ins` - 获取打卡历史
- `GET /api/betting-plans/{planId}/progress` - 获取进度统计

### 支付
- `POST /api/payments/charge` - 充值（Stripe）
- `POST /api/payments/withdraw` - 提现
- `GET /api/users/{userId}/balance` - 获取余额

### 结算
- `GET /api/settlement-check` - 检查计划是否可结算
- `GET /api/settlements/{settlementId}` - 获取结算详情
- `POST /api/settlements/{planId}/execute` - 执行结算

### 通知
- `POST /api/notifications/register-device` - 注册设备令牌
- `POST /api/notifications/test` - 发送测试通知

## 性能指标

## 核心业务逻辑

### 对赌计划生命周期

1. **创建阶段** (PENDING)
   - 创建者发起计划，设置赌金、时间范围、目标体重
   - 系统自动冻结创建者账户中的赌金
   - 可邀请好友参与（每个计划仅限一次邀请）

2. **待接受阶段** (PENDING → WAITING_DOUBLE_CHECK)
   - 被邀请人可以接受或拒绝计划
   - 如拒绝，解冻创建者资金，计划终止
   - 如接受，进入待双方确认目标状态

3. **确认目标阶段** (WAITING_DOUBLE_CHECK → ACTIVE)
   - 参与者输入自己的初始体重和目标体重
   - 双方确认后，计划正式激活
   - 系统冻结参与者资金

4. **进行中阶段** (ACTIVE)
   - 双方每日打卡记录体重
   - 可查看进度统计和对比
   - 允许放弃计划（中途退出）

5. **结算阶段** (COMPLETED)
   - 计划到期后，检查打卡数据
   - 双方提交结算选择（达成/未达成）
   - 匹配双方选择并执行结算：
     - 双方都达成 → 原路返还（无手续费）
     - 双方都未达成 → 扣除 10% 手续费后平分
     - 一方达成 → 获得全部赌金
     - 选择不匹配 → 最多 3 轮后进入仲裁

6. **终止情况**
   - CANCELLED: 创建者取消计划（解冻资金）
   - REJECTED: 被邀请人拒绝计划（解冻资金）
   - EXPIRED: 超时未接受（解冻资金）
   - 放弃待接受计划：原路返还
   - 放弃进行中计划：判负，资金转给对方

### 资金管理机制

- **冻结**: 创建计划和接受计划时自动冻结对应赌金
- **解冻**: 计划取消/拒绝/过期时自动解冻
- **划转**: 结算后将资金从平台账户转入用户账户
- **手续费**: 
  - 正常结算：0%
  - 双输情况：10%
  - 仲裁强制结算：15%

## 数据模型

### 核心表结构

1. **users (用户表)**
   - id, email, nickname, password_hash
   - balance (可用余额), frozen_balance (冻结金额)
   - created_at, updated_at

2. **betting_plans (对赌计划表)**
   - id, creator_id, participant_id
   - status (pending/waiting_double_check/active/completed/cancelled/rejected/expired)
   - bet_amount, start_date, end_date, description
   - creator/participant 的 initial_weight, target_weight, target_weight_loss
   - activated_at, abandoned_by, abandoned_at

3. **check_ins (打卡记录表)**
   - id, user_id, plan_id
   - weight (当前体重)
   - check_in_date, created_at

4. **invitations (邀请表)**
   - id, plan_id, inviter_id, invitee_id
   - status (pending/accepted/rejected)
   - sent_at, responded_at

5. **settlements (结算记录表)**
   - id, plan_id
   - creator_final_weight, participant_final_weight
   - creator_achieved, participant_achieved
   - creator_amount, participant_amount, platform_fee
   - settlement_date, status

6. **settlement_choices (结算选择表)**
   - id, plan_id, user_id
   - choice (achieved/failed)
   - submitted_at

7. **transactions (交易记录表)**
   - id, user_id, amount, type (charge/withdraw/bet/refund/freeze/unfreeze)
   - balance_before, balance_after
   - related_plan_id, created_at

8. **device_tokens (设备令牌表)**
   - id, user_id, device_token, platform (ios/android)
   - created_at

## 环境要求

### 后端
- Python 3.14+
- PostgreSQL 14+ (开发环境可用 SQLite)
- Redis 7+

### Android
- Android Studio Hedgehog (2023.1.1) 或更高版本
- JDK 17
- Android SDK (API 24-34)

### iOS
- Xcode 15.0+
- iOS 14.0+
- CocoaPods 1.12+

## 开发指南

### 本地开发环境搭建

#### 后端

```bash
cd backend

# 1. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库连接、JWT 密钥等配置

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/api/docs 查看 API 文档

#### Android

1. 使用 Android Studio 打开 `android/` 目录
2. 同步 Gradle 依赖
3. 配置 API 地址：
   - 编辑 `app/src/main/java/com/weightloss/betting/di/NetworkModule.kt`
   - 修改 `BASE_URL` 为实际的后端地址（模拟器用 `http://10.0.2.2:8000`）
4. 运行应用到设备或模拟器

#### iOS

```bash
cd ios

# 1. 安装 CocoaPods 依赖
pod install

# 2. 打开工作空间
open WeightLossBetting.xcworkspace

# 3. 配置 API 地址
# 在 Xcode 中打开 Data/Network/APIService.swift
# 修改 baseURL 为实际的后端地址

# 4. 运行项目
# 选择目标设备或模拟器，点击 Run 按钮
```

### 测试

#### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_betting_plan_service.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

#### Android 测试

```bash
cd android

# 运行单元测试
./gradlew test

# 运行仪器测试
./gradlew connectedAndroidTest
```

#### iOS 测试

```bash
cd ios
xcodebuild test -scheme WeightLossBetting
```

### 代码质量

#### Python 代码检查和格式化

```bash
cd backend

# 代码格式化
black app/

# 导入排序
isort app/

# 类型检查
mypy app/

# 代码检查
pylint app/
```

#### Android 代码检查

```bash
cd android
./gradlew lint
```

#### iOS 代码检查

```bash
swiftlint
```

## 生产环境部署

### 后端部署

#### Docker 部署（推荐）

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 建议配置

- **应用服务器**: Docker + Uvicorn + Gunicorn
- **数据库**: AWS RDS PostgreSQL / Google Cloud SQL
- **缓存**: AWS ElastiCache Redis / Google Cloud Memorystore
- **存储**: AWS S3 / Google Cloud Storage（体重秤照片）
- **CDN**: CloudFront / Cloud CDN
- **监控**: Sentry + Prometheus + Grafana
- **负载均衡**: Nginx / ALB

### 环境变量配置（生产环境）

```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# JWT 密钥
SECRET_KEY=your-super-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx

# Firebase
FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json

# 生产环境配置
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
```

## 安全措施

- ✅ 密码使用 bcrypt 哈希
- ✅ JWT 令牌安全配置（HS256 算法）
- ✅ HTTPS/TLS 加密通信
- ✅ SQL 注入防护（参数化查询）
- ✅ XSS 和 CSRF 防护
- ✅ API 限流（100 req/min）
- ✅ 支付安全（PCI DSS 合规）
- ✅ 请求验证（Pydantic Schema）
- ✅ 统一错误处理

## 性能优化

### 后端优化

- 数据库索引优化
- Redis 缓存热点数据
- 异步 I/O 操作
- 数据库连接池
- GZip 压缩响应

### 移动端优化

- 图片懒加载和缓存
- 分页加载数据
- 离线模式支持
- 网络请求合并

## 许可证

MIT License

## 项目状态与路线图

### 已完成功能 ✅

- [x] 用户认证系统（注册、登录、JWT 令牌管理）
- [x] 对赌计划创建和管理
- [x] 邀请系统（邮箱搜索、发送邀请、接受/拒绝）
- [x] 打卡签到系统
- [x] 支付集成（Stripe）
- [x] 结算系统（三次选择匹配机制）
- [x] 仲裁系统
- [x] 通知推送（FCM + APNs）
- [x] 资金管理（冻结/解冻/划转）
- [x] Android 客户端基础架构
- [x] iOS 客户端基础架构

### 进行中功能 🚧

- [ ] Google OAuth 第三方登录
- [ ] 完整的 UI 界面实现

### 待开发功能 📋

- [ ] 群组挑战模式
- [ ] 多语言支持

## 常见问题 FAQ

### Q: 如何重置本地数据库？

```bash
cd backend
rm -f app.db  # 删除 SQLite 数据库文件
python init_db.py  # 重新初始化
```

### Q: 如何查看 API 文档？

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Q: Android 模拟器无法连接后端？

Android 模拟器使用 `http://10.0.2.2:8000` 访问本机后端。
真机测试需要将设备与电脑置于同一网络，并使用电脑的 IP 地址。

### Q: 如何运行测试？

```bash
# 后端
cd backend
pytest

# Android
cd android
./gradlew test

# iOS
cd ios
xcodebuild test -scheme WeightLossBetting
```

### Q: 结算时双方选择不匹配怎么办？

系统会自动进入仲裁流程，最多进行 3 轮选择。如果仍然不匹配，将启动强制仲裁，扣除 15% 的手续费后根据打卡数据判定。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 Bug

请提供：
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（OS、版本号等）

### 功能建议

请描述：
- 功能需求
- 使用场景
- 期望效果

## 技术支持

如有问题，请通过以下方式联系：

- 📧 Email: support@weightloss-betting.com
- 💬 提交 Issue
- 📖 查阅各子模块的 README 文档

---

**项目状态**: ✅ Demo 已完成  
**技术验证**: ✅ 通过  
**可演示**: ✅ 是  
**最后更新**: 2026-04-04
