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
- `POST /api/auth/google` - Google 登录

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

## 许可证

MIT
