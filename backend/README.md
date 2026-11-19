# Weight Loss Betting API - 后端服务

减肥对赌 APP 的后端 API 服务,使用 FastAPI 框架构建。

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 7+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (python-jose)
- **支付**: Stripe
- **日志**: Loguru

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── redis_client.py      # Redis 客户端
│   ├── logger.py            # 日志配置
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模式
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   ├── middleware/          # 中间件
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── tests/                   # 测试文件
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量示例
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,填写数据库、Redis、Stripe 等配置
```

### 3. 初始化数据库

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动

- API 文档: http://localhost:8000/api/docs
- ReDoc 文档: http://localhost:8000/api/redoc

## 开发指南

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black app/
isort app/
```

### 类型检查

```bash
mypy app/
```

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `POST /api/auth/logout` - 吊销 Refresh Token（提交令牌时生效）
- `POST /api/auth/google` - Google 登录

真实支付接口：

- `POST /api/payments/charge/intent` - 创建 Stripe PaymentIntent，客户端 PaymentSheet 确认后由 Webhook 入账
- `POST /api/payments/stripe/webhook` - 验证 Stripe 签名并完成充值入账
- `POST /api/payments/connect/onboarding` - 创建 Stripe Connect Express 提现账户认证链接

后台提现恢复接口：

- `GET /api/admin/payouts/pending` - 查看所有仍处于 pending 的提现，包括待创建 Payout 和待对账 Payout
- `POST /api/admin/payouts/{transaction_id}/retry` - 重试缺失 Transfer/Payout 的提现
- `POST /api/admin/payouts/{transaction_id}/reconcile` - 从 Stripe 查询 Payout 状态，恢复丢失 Webhook 的提现

开发环境默认 `PAYMENT_PROVIDER=demo`，旧的 `/api/payments/charge` 保留为本地演示接口。
生产环境设置 `PAYMENT_PROVIDER=stripe`，并配置 Stripe 密钥、Webhook 密钥、Connect 国家代码和币种；不要把演示接口暴露给生产用户。使用 PostgreSQL 等生产数据库启动时，应用会拒绝开发 JWT 密钥、本地 CORS 地址、Stripe 占位密钥、非 HTTPS Connect 回调地址、非法国家/币种代码以及当前金额换算不支持的零小数/特殊出款币种。Stripe 平台国家、Connected Account 国家、银行账户和结算币种仍需在 Stripe 测试环境中确认匹配。
登录、注册、刷新令牌和 Google 登录接口使用独立的每 IP 限流窗口，默认每分钟最多 20 次。
Stripe 模式下提现会先预留余额，再创建 Connect Transfer/Payout；只有 `payout.paid` Webhook 到达后才完成扣账，失败会释放预留余额。若 Transfer 已成功但 Payout 创建失败，交易保持 pending，等待重试或对账，不会错误释放资金。

### 用户
- `GET /api/users/{userId}` - 获取用户信息
- `PUT /api/users/{userId}` - 更新用户信息
- `POST /api/users/{userId}/payment-methods` - 绑定支付方式

### 对赌计划
- `POST /api/betting-plans` - 创建对赌计划
- `GET /api/betting-plans/{planId}` - 获取计划详情
- `POST /api/betting-plans/{planId}/accept` - 接受计划
- `POST /api/betting-plans/{planId}/reject` - 拒绝计划

### 打卡
- `POST /api/check-ins` - 创建打卡记录
- `GET /api/betting-plans/{planId}/check-ins` - 获取打卡历史
- `GET /api/betting-plans/{planId}/progress` - 获取进度统计

### 支付
- `POST /api/payments/charge` - 充值
- `POST /api/payments/withdraw` - 提现
- `GET /api/users/{userId}/balance` - 获取余额
- `GET /api/users/{userId}/transactions` - 获取交易历史

### 结算
- `GET /api/settlements/{settlementId}` - 获取结算详情

### 社交
- `GET /api/leaderboard/{type}` - 获取排行榜
- `POST /api/betting-plans/{planId}/comments` - 发表评论
- `GET /api/users/{userId}/badges` - 获取勋章

## 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| DATABASE_URL | PostgreSQL 连接字符串 | postgresql://user:pass@localhost:5432/db |
| REDIS_URL | Redis 连接字符串 | redis://localhost:6379/0 |
| SECRET_KEY | JWT 密钥 | your-secret-key |
| STRIPE_SECRET_KEY | Stripe 密钥 | sk_test_xxx |
| GOOGLE_CLIENT_IDS | Google Web/Android/iOS Client ID，逗号分隔 | xxx.apps.googleusercontent.com |
| ALLOWED_HOSTS | 生产 API 域名，逗号分隔 | api.example.com |
| FIREBASE_CREDENTIALS_PATH | FCM 服务账号 JSON 路径 | /run/secrets/firebase.json |
| FCM_PROJECT_ID | Firebase 项目 ID | weight-bet-prod |
| APNS_KEY_ID | APNs Auth Key ID | ABC123DEFG |
| APNS_TEAM_ID | Apple Developer Team ID | TEAM123 |
| APNS_PRIVATE_KEY_PATH | APNs `.p8` 私钥路径 | /run/secrets/AuthKey.p8 |
| APNS_BUNDLE_ID | iOS Bundle ID | com.weightloss.betting |
| ENVIRONMENT | 运行环境（development/staging/production） | production |

通知发送说明：设备令牌注册后，后端会按平台调用 FCM HTTP v1 或 APNs Provider API；未配置对应凭据时会返回失败状态，不会把“仅写日志”报告为发送成功。服务账号 JSON、APNs 私钥和 Google 配置文件都不能提交到 Git。

## 许可证

MIT
