# 跨平台集成测试

## 目录结构

```
tests/integration/
├── README.md                      # 本文件
├── test_cross_platform.py         # 自动化测试脚本
├── run_integration_tests.sh       # Bash 执行脚本
└── run_integration_tests.ps1      # PowerShell 执行脚本
```

## 测试概述

本目录包含减肥对赌 APP 的跨平台集成测试,用于验证 Android、iOS 和后端 API 之间的数据互通和功能一致性。

## 测试场景

### 自动化测试 (10 个场景)

1. **跨平台用户注册和登录**
   - 验证用户可以在一个平台注册,在另一个平台登录
   - 测试 JWT 令牌在两个平台上的有效性

2. **跨平台创建和接受对赌计划**
   - Android 创建计划 → iOS 接受
   - 验证计划状态转换和资金冻结

3. **跨平台打卡和进度同步**
   - iOS 打卡 → Android 查看
   - 验证进度计算和数据同步

4. **跨平台支付流程**
   - 验证余额查询一致性
   - 验证交易历史同步

5. **跨平台社交功能**
   - 评论同步测试
   - 排行榜一致性测试

6. **数据一致性测试**
   - 多次请求数据一致性验证
   - 并发访问测试

7. **API 响应时间测试**
   - P95 响应时间 < 200ms
   - 性能基准测试

8. **结算流程测试** (4 个子场景)
   - 双方都达成目标的结算
   - 双方都未达成目标的结算
   - 创建者达成目标的结算
   - 参与者达成目标的结算
   - 跨平台结算一致性

9. **支付流程测试** (7 个子场景)
   - 余额查询一致性
   - 交易历史同步
   - 充值流程测试
   - 提现流程测试
   - 资金冻结和解冻
   - 跨平台余额同步
   - 交易原子性

10. **通知功能测试** (手动测试指南)
    - 计划邀请通知
    - 计划生效通知
    - 打卡提醒通知
    - 结算通知
    - 通知权限处理
    - 跨平台通知一致性
    - 通知历史同步

## 快速开始

### 前提条件

1. Python 3.8+
2. 后端服务运行在 http://localhost:8000
3. PostgreSQL 和 Redis 正常运行

### 安装依赖

```bash
pip install pytest requests pytest-html
```

### 运行测试

**Linux/Mac**:
```bash
chmod +x run_integration_tests.sh
./run_integration_tests.sh
```

**Windows**:
```powershell
.\run_integration_tests.ps1
```

**直接使用 pytest**:
```bash
pytest test_cross_platform.py -v
```

### 查看报告

测试报告会生成在项目根目录的 `test_reports/` 文件夹:
```
test_reports/integration_test_report_YYYYMMDD_HHMMSS.html
```

## 测试配置

### API 基础 URL

默认: `http://localhost:8000/api`

修改方法:
```python
# 在 test_cross_platform.py 中修改
@pytest.fixture(scope="class")
def api_base_url(self):
    return "http://your-api-server:8000/api"
```

### 测试用户

默认测试用户:
- Android 用户: test_android@example.com
- iOS 用户: test_ios@example.com
- 密码: Test123456!

修改方法:
```python
# 在 test_cross_platform.py 中修改 test_users fixture
```

## 测试数据清理

### 清理测试数据

```bash
# 清理所有数据
python manage.py flush --no-input

# 或删除特定测试用户
python manage.py shell
>>> from app.models import User
>>> User.objects.filter(email__contains='test_').delete()
```

### 重置数据库

```bash
# 删除并重建数据库
python manage.py migrate --run-syncdb
```

## 高级用法

### 运行特定测试

```bash
# 运行单个测试
pytest test_cross_platform.py::TestCrossPlatform::test_scenario_1_cross_platform_auth -v

# 运行多个测试
pytest test_cross_platform.py -k "auth or payment" -v
```

### 生成详细报告

```bash
pytest test_cross_platform.py \
    -v \
    --html=detailed_report.html \
    --self-contained-html \
    --tb=long \
    --capture=no
```

### 并行执行

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行运行 (4 个进程)
pytest test_cross_platform.py -n 4
```

### 调试模式

```bash
# 显示 print 输出
pytest test_cross_platform.py -s

# 在失败时进入调试器
pytest test_cross_platform.py --pdb

# 详细输出
pytest test_cross_platform.py -vv
```

## 性能基准

### 响应时间目标

| 端点 | P95 目标 |
|------|---------|
| GET /api/users/me | < 200ms |
| POST /api/betting-plans | < 200ms |
| POST /api/check-ins | < 500ms |
| GET /api/leaderboard/* | < 200ms |

### 同步延迟目标

| 操作 | 目标 |
|------|-----|
| 创建计划 | < 1s |
| 接受计划 | < 1s |
| 打卡记录 | < 1s |
| 余额更新 | < 1s |

## 常见问题

### Q: 测试失败: 后端服务未运行

**A**: 确保后端服务运行在 http://localhost:8000
```bash
cd backend
python manage.py runserver
```

### Q: 测试失败: 用户已存在

**A**: 测试会自动处理已存在的用户。如需重置:
```bash
python manage.py flush --no-input
```

### Q: 测试失败: 数据库连接错误

**A**: 确保 PostgreSQL 和 Redis 正常运行
```bash
# PostgreSQL
sudo service postgresql start

# Redis
sudo service redis start

# 或使用 Docker
docker-compose up -d
```

### Q: 如何跳过某些测试?

**A**: 使用 pytest 标记
```python
@pytest.mark.skip(reason="需要真机设备")
def test_notification():
    pass
```

运行时跳过:
```bash
pytest test_cross_platform.py -m "not slow"
```

## 持续集成

### GitHub Actions 示例

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests pytest-html
      
      - name: Run migrations
        run: |
          cd backend
          python manage.py migrate
      
      - name: Start backend
        run: |
          cd backend
          python manage.py runserver &
          sleep 5
      
      - name: Run tests
        run: |
          pytest tests/integration/test_cross_platform.py -v
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: test_reports/
```

## 贡献指南

### 添加新测试

1. 在 `TestCrossPlatform` 类中添加新方法
2. 方法名以 `test_` 开头
3. 使用清晰的文档字符串描述测试目的
4. 使用 assert 语句验证结果
5. 添加 print 语句输出测试结果

示例:
```python
def test_new_feature(self, api_base_url, user_tokens):
    """
    测试新功能
    
    验证新功能在两个平台上的一致性
    """
    headers = {"Authorization": f"Bearer {user_tokens['user_a']}"}
    
    # 执行测试
    response = requests.get(f"{api_base_url}/new-endpoint", headers=headers)
    
    # 验证结果
    assert response.status_code == 200
    data = response.json()
    assert data["field"] == "expected_value"
    
    print("✅ 新功能测试通过")
```

### 代码风格

- 遵循 PEP 8 规范
- 使用有意义的变量名
- 添加适当的注释
- 保持测试独立性

## 相关文档

- [跨平台集成测试计划](../../CROSS_PLATFORM_INTEGRATION_TEST_PLAN.md)
- [测试报告模板](../../INTEGRATION_TEST_REPORT_TEMPLATE.md)
- [快速开始指南](../../INTEGRATION_TEST_QUICK_START.md)
- [实现总结](../../PHASE_4_IMPLEMENTATION_SUMMARY.md)

## 许可证

本测试代码遵循项目主许可证。

---

**最后更新**: 2024
**维护者**: Kiro AI Assistant
