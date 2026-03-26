# 后端启动指南

## 当前状态

后端服务尝试启动时遇到依赖安装问题。

## 问题分析

1. ❌ `psycopg2-binary` 安装失败 - 需要 PostgreSQL 开发库
2. ⚠️ 需要配置数据库连接
3. ⚠️ 需要配置 Redis 连接

## 解决方案

### 方案 1: 使用 Docker (推荐)

这是最简单的方式，可以避免本地环境配置问题。

#### 1. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: weightloss
      POSTGRES_PASSWORD: weightloss123
      POSTGRES_DB: weight_loss_betting
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # FastAPI 后端
  backend:
    build: .
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://weightloss:weightloss123@postgres:5432/weight_loss_betting
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
      - DEBUG=True
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

#### 2. 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

---

### 方案 2: 本地安装 (需要配置环境)

#### 1. 安装 PostgreSQL

**Windows**:
- 下载并安装 PostgreSQL: https://www.postgresql.org/download/windows/
- 安装时记住设置的密码
- 确保 PostgreSQL 服务正在运行

**创建数据库**:
```bash
# 使用 psql 连接
psql -U postgres

# 创建数据库和用户
CREATE DATABASE weight_loss_betting;
CREATE USER weightloss WITH PASSWORD 'weightloss123';
GRANT ALL PRIVILEGES ON DATABASE weight_loss_betting TO weightloss;
\q
```

#### 2. 安装 Redis

**Windows**:
- 下载 Redis for Windows: https://github.com/microsoftarchive/redis/releases
- 或使用 WSL2 安装 Redis
- 或使用 Docker 运行 Redis:
  ```bash
  docker run -d -p 6379:6379 redis:7-alpine
  ```

#### 3. 修复 Python 依赖

**选项 A: 使用预编译的 psycopg2-binary**

修改 `requirements.txt`，将 `psycopg2-binary==2.9.9` 改为:
```
psycopg2-binary>=2.9.0
```

然后重新安装:
```bash
pip install --upgrade pip
pip install psycopg2-binary --no-build-isolation
```

**选项 B: 使用 psycopg (推荐)**

修改 `requirements.txt`，将 `psycopg2-binary==2.9.9` 替换为:
```
psycopg[binary]==3.1.13
```

这是新版本的 PostgreSQL 适配器，更容易安装。

#### 4. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 5. 配置环境变量

编辑 `.env` 文件:
```bash
DATABASE_URL=postgresql://weightloss:weightloss123@localhost:5432/weight_loss_betting
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### 6. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head
```

#### 7. 启动服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 方案 3: 使用 SQLite (快速测试)

如果只是想快速测试，可以暂时使用 SQLite 代替 PostgreSQL。

#### 1. 修改依赖

在 `requirements.txt` 中注释掉 PostgreSQL 相关依赖:
```
# psycopg2-binary==2.9.9
```

#### 2. 修改配置

在 `.env` 文件中:
```bash
DATABASE_URL=sqlite:///./weight_loss_betting.db
REDIS_URL=redis://localhost:6379/0  # 或者注释掉，使用内存缓存
SECRET_KEY=dev-secret-key
DEBUG=True
```

#### 3. 修改代码

在 `app/database.py` 中，如果使用 SQLite，需要添加:
```python
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
```

#### 4. 安装依赖并启动

```bash
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 验证服务

服务启动后，访问以下 URL 验证:

- **健康检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/api/docs
- **ReDoc 文档**: http://localhost:8000/api/redoc

## 常见问题

### 1. 端口被占用

```bash
# Windows 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程
taskkill /PID <进程ID> /F
```

### 2. 数据库连接失败

- 检查 PostgreSQL 服务是否运行
- 检查数据库连接字符串是否正确
- 检查防火墙设置

### 3. Redis 连接失败

- 检查 Redis 服务是否运行
- 尝试使用 `redis-cli ping` 测试连接

### 4. 依赖安装失败

- 更新 pip: `python -m pip install --upgrade pip`
- 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
- 尝试使用虚拟环境

## 推荐的开发流程

1. ✅ 使用 Docker Compose (最简单)
2. ✅ 本地安装 PostgreSQL + Redis (完整功能)
3. ✅ 使用 SQLite (快速测试)

## 下一步

服务启动后，你可以:

1. 访问 API 文档测试接口
2. 运行单元测试: `pytest`
3. 运行集成测试: `pytest tests/integration/`
4. 启动 Android/iOS 客户端连接后端

---

**需要帮助?** 

- 查看 README.md 了解更多信息
- 查看 API 文档了解接口详情
- 运行测试确保功能正常
