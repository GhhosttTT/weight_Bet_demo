# 性能测试计划

## 测试目标

验证减肥对赌 APP 后端系统在高负载下的性能表现,确保满足以下性能需求:
- API 响应时间 < 200ms (P95)
- 打卡操作 < 500ms
- 结算计算 < 1s
- 支持 10,000+ 并发用户
- 数据库查询 < 100ms

## 测试工具

- **Locust**: 负载测试和压力测试
- **Apache Bench (ab)**: 简单的性能基准测试
- **PostgreSQL EXPLAIN ANALYZE**: 数据库查询性能分析
- **Redis Monitor**: 缓存性能监控

## 测试场景

### 场景 1: 基准性能测试

**目标**: 测试单个 API 端点的基准性能

**测试步骤**:
```bash
# 测试用户信息查询
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
   http://localhost:8000/api/users/123

# 测试计划列表查询
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
   http://localhost:8000/api/users/123/betting-plans
```

**预期结果**:
- 平均响应时间 < 100ms
- P95 响应时间 < 200ms
- 错误率 < 0.1%

### 场景 2: 负载测试

**目标**: 测试系统在正常负载下的表现

**测试配置**:
- 并发用户数: 100
- 持续时间: 10 分钟
- 用户行为: 模拟真实用户操作(查看、创建、打卡)

**执行命令**:
```bash
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=100 \
       --spawn-rate=10 \
       --run-time=10m \
       --headless
```

**预期结果**:
- 平均响应时间 < 150ms
- P95 响应时间 < 200ms
- 吞吐量 > 500 req/s
- 错误率 < 1%

### 场景 3: 压力测试

**目标**: 找到系统的性能瓶颈和极限

**测试配置**:
- 并发用户数: 逐步增加 100 → 500 → 1000 → 5000
- 每个阶段持续: 5 分钟
- 观察系统崩溃点

**执行命令**:
```bash
# 阶段 1: 100 用户
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users=100 --spawn-rate=10 --run-time=5m --headless

# 阶段 2: 500 用户
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users=500 --spawn-rate=50 --run-time=5m --headless

# 阶段 3: 1000 用户
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users=1000 --spawn-rate=100 --run-time=5m --headless

# 阶段 4: 5000 用户
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users=5000 --spawn-rate=500 --run-time=5m --headless
```

**监控指标**:
- CPU 使用率
- 内存使用率
- 数据库连接数
- Redis 内存使用
- 响应时间分布
- 错误率

### 场景 4: 峰值测试

**目标**: 测试系统在短时间内处理大量请求的能力

**测试配置**:
- 并发用户数: 2000
- 持续时间: 2 分钟
- 快速启动: spawn-rate=500

**执行命令**:
```bash
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=2000 \
       --spawn-rate=500 \
       --run-time=2m \
       --headless
```

**预期结果**:
- 系统不崩溃
- 响应时间增加但仍可接受 (< 500ms)
- 错误率 < 5%

### 场景 5: 持久性测试

**目标**: 测试系统长时间运行的稳定性

**测试配置**:
- 并发用户数: 200
- 持续时间: 2 小时
- 模拟真实用户行为

**执行命令**:
```bash
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=200 \
       --spawn-rate=20 \
       --run-time=2h \
       --headless
```

**监控指标**:
- 内存泄漏检测
- 数据库连接池状态
- 缓存命中率变化
- 响应时间趋势

## 数据库性能测试

### 查询性能分析

```sql
-- 分析用户查询性能
EXPLAIN ANALYZE
SELECT * FROM users WHERE id = '123';

-- 分析计划列表查询性能
EXPLAIN ANALYZE
SELECT * FROM betting_plans 
WHERE creator_id = '123' OR participant_id = '123'
ORDER BY created_at DESC
LIMIT 20;

-- 分析打卡历史查询性能
EXPLAIN ANALYZE
SELECT * FROM check_ins 
WHERE plan_id = '456' AND user_id = '123'
ORDER BY check_in_date DESC;

-- 分析排行榜查询性能
EXPLAIN ANALYZE
SELECT u.id, u.nickname, SUM(c.weight_loss) as total_weight_loss
FROM users u
JOIN check_ins c ON u.id = c.user_id
GROUP BY u.id, u.nickname
ORDER BY total_weight_loss DESC
LIMIT 100;
```

### 索引优化建议

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_betting_plans_creator ON betting_plans(creator_id);
CREATE INDEX idx_betting_plans_participant ON betting_plans(participant_id);
CREATE INDEX idx_betting_plans_status ON betting_plans(status);
CREATE INDEX idx_check_ins_plan_user ON check_ins(plan_id, user_id);
CREATE INDEX idx_check_ins_date ON check_ins(check_in_date);
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_settlements_plan ON settlements(plan_id);

-- 复合索引
CREATE INDEX idx_betting_plans_user_status ON betting_plans(creator_id, status);
CREATE INDEX idx_check_ins_plan_date ON check_ins(plan_id, check_in_date);
```

## 缓存性能测试

### Redis 监控

```bash
# 启动 Redis 监控
redis-cli monitor

# 查看缓存命中率
redis-cli info stats | grep keyspace

# 查看内存使用
redis-cli info memory
```

### 缓存策略验证

1. **用户信息缓存** (TTL: 10分钟)
   - 首次查询: 从数据库读取
   - 后续查询: 从缓存读取
   - 验证缓存命中率 > 90%

2. **计划详情缓存** (TTL: 5分钟)
   - 验证缓存命中率 > 80%

3. **排行榜缓存** (TTL: 5分钟)
   - 验证缓存命中率 > 95%

## 性能优化建议

### 1. 数据库优化
- ✅ 添加必要的索引
- ✅ 使用连接池 (min: 10, max: 50)
- ✅ 启用查询缓存
- ⚠️ 考虑读写分离
- ⚠️ 考虑数据分区

### 2. 缓存优化
- ✅ 实现 Redis 缓存
- ✅ 设置合理的 TTL
- ⚠️ 实现缓存预热
- ⚠️ 实现缓存降级策略

### 3. API 优化
- ✅ 实现响应压缩 (gzip)
- ✅ 实现分页
- ⚠️ 实现 GraphQL (按需查询)
- ⚠️ 实现 API 版本控制

### 4. 异步处理
- ✅ 异步发送通知
- ✅ 异步处理图片上传
- ⚠️ 使用消息队列 (RabbitMQ/Kafka)
- ⚠️ 实现后台任务队列

### 5. 负载均衡
- ⚠️ 部署多个应用实例
- ⚠️ 使用 Nginx 负载均衡
- ⚠️ 实现健康检查

## 测试报告模板

### 性能测试报告

**测试日期**: YYYY-MM-DD  
**测试环境**: 
- 服务器配置: 4 Core CPU, 8GB RAM
- 数据库: PostgreSQL 14
- 缓存: Redis 7

**测试结果**:

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| API 响应时间 (P95) | < 200ms | XXX ms | ✅/❌ |
| 打卡操作响应时间 | < 500ms | XXX ms | ✅/❌ |
| 结算计算时间 | < 1s | XXX ms | ✅/❌ |
| 并发用户数 | 10,000+ | XXX | ✅/❌ |
| 数据库查询时间 | < 100ms | XXX ms | ✅/❌ |
| 吞吐量 | > 500 req/s | XXX req/s | ✅/❌ |
| 错误率 | < 1% | XX% | ✅/❌ |

**性能瓶颈**:
1. [描述发现的瓶颈]
2. [描述发现的瓶颈]

**优化建议**:
1. [优化建议]
2. [优化建议]

**结论**:
[总体评估和建议]

## 执行清单

- [ ] 安装性能测试工具 (Locust, ab)
- [ ] 准备测试环境和数据
- [ ] 执行基准性能测试
- [ ] 执行负载测试
- [ ] 执行压力测试
- [ ] 执行峰值测试
- [ ] 执行持久性测试
- [ ] 分析数据库查询性能
- [ ] 验证缓存性能
- [ ] 生成性能测试报告
- [ ] 实施优化建议
- [ ] 重新测试验证优化效果
