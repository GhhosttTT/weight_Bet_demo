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
- **框架**: FastAPI (Python 3.14)
- **数据库**: SQLite/PostgreSQL
- **ORM**: SQLAlchemy + Alembic
- **缓存**: Redis
- **支付**: Stripe SDK
- **认证**: JWT (python-jose) + bcrypt
- **通知**: Firebase Cloud Messaging + APNs

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
- ✅ 创建减肥对赌计划（设置赌金、时长、目标）
- ✅ 邮箱搜索好友并邀请
- ✅ 待接受状态管理和二次确认
- ✅ 计划状态流转（pending → active → completed/expired/cancelled）
- ✅ 资金冻结和解冻

### 3. 打卡签到
- ✅ 每日体重打卡


### 4. 支付与资金管理
-  Stripe 支付集成


### 5. 结算系统
- ✅ App 检查触发机制
- ✅ 三次选择匹配机制：
  - 双方都达成 → 原路返还（无手续费）
  - 双方都未达成 → 扣除 10% 手续费后平分
  - 一方达成 → 获得全部赌金
  - 不匹配 → 最多 3 轮后仲裁
- ✅ 超时处理（24 小时倒计时）
- ✅ 强制仲裁（扣 15% 费用）

### 6. 邀请与放弃计划
- ✅ 好友邀请（每个计划限一次）
- ✅ 放弃待接受计划（原路返还）
- ✅ 放弃进行中计划（判负，资金转给对方）

### 7. 通知系统
- ✅ Firebase Cloud Messaging (Android)
- ✅ Apple Push Notification Service (iOS)
- ✅ 场景：邀请、计划生效、结算完成、打卡提醒



## 项目结构

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
- `POST /api/auth/google` - Google 登录
- `POST /api/auth/refresh` - 刷新令牌

### 对赌计划
- `POST /api/betting-plans` - 创建计划
- `GET /api/betting-plans/{planId}` - 获取计划详情
- `POST /api/betting-plans/{planId}/invite` - 邀请参与者
- `POST /api/betting-plans/{planId}/accept` - 接受计划

### 打卡
- `POST /api/check-ins` - 创建打卡记录
- `GET /api/betting-plans/{planId}/check-ins` - 获取打卡历史
- `GET /api/betting-plans/{planId}/progress` - 获取进度统计

### 支付
- `GET /api/users/{userId}/balance` - 获取余额
- `POST /api/payments/charge` - 充值
- `POST /api/payments/withdraw` - 提现

### 结算
- `GET /api/settlement-check` - 检查结算日
- `GET /api/settlements/{settlementId}` - 获取结算详情

## 性能指标

### 后端性能
- API 响应时间：< 200ms (P95)
- 打卡操作：< 500ms
- 结算计算：< 1s
- 并发用户：支持 10,000+

### 移动端性能
- 启动时间：< 2s
- 内存占用：< 150MB
- 帧率：> 55 FPS
- 网络请求：< 500ms

## 安全措施

- ✅ 密码使用 bcrypt 哈希
- ✅ JWT 令牌安全配置
- ✅ HTTPS/TLS 加密通信
- ✅ SQL 注入防护（参数化查询）
- ✅ XSS 和 CSRF 防护
- ✅ API 限流（100 req/min）
- ✅ 支付安全（PCI DSS 合规）

## 开发工具

### 测试
```bash
# 后端测试
cd backend
pytest

# Android 测试
cd android
./gradlew test

# iOS 测试
cd ios
xcodebuild test -scheme WeightLossBetting
```

### 代码质量
```bash
# Python 代码检查和格式化
pylint backend/app
black backend/app

# Android 代码检查
./gradlew lint

# iOS 代码检查
swiftlint
```

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

## 生产环境部署

### 建议配置
- **后端**: Docker + Uvicorn + Gunicorn
- **数据库**: AWS RDS PostgreSQL / Google Cloud SQL
- **缓存**: AWS ElastiCache Redis / Google Cloud Memorystore
- **存储**: AWS S3 / Google Cloud Storage（体重秤照片）
- **CDN**: CloudFront / Cloud CDN
- **监控**: Sentry + Prometheus + Grafana

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

---

**项目状态**: ✅ Demo 已完成  
**技术验证**: ✅ 通过  
**可演示**: ✅ 是
