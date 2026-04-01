# 合并 Bugfix 文档

## 概述

本文档合并了减肥对赌 APP 的所有 bugfix，包括：
- 充值后余额未更新 Bug 修复
- 推荐系统日期序列化 Bug 修复
- 推荐系统 Redis 缓存 Bug 修复
- 连接超时问题修复

---

## Bug 1: 充值后余额未更新

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

### 根本原因假设

基于 bug 描述和代码分析，最可能的根本原因是：

1. **后端充值接口实现缺陷**: `/api/payments/charge` 接口在处理充值请求时，可能只是创建了充值订单记录或调用了第三方支付网关，但没有在数据库中更新用户的 `availableBalance` 字段。接口返回成功响应，但实际的余额更新逻辑缺失或未执行。

2. **数据库事务未提交**: 后端可能在事务中更新了余额，但由于某种原因（异常、事务回滚、未显式提交）导致更新未持久化到数据库。

3. **异步处理问题**: 后端可能将余额更新放在异步任务中处理，但异步任务执行失败或延迟过长，导致用户立即查询时看不到更新。

4. **缓存不一致**: 虽然数据库已更新，但客户端或服务端的缓存层未刷新，导致查询时返回旧的缓存数据。但根据代码分析，`getBalance()` 方法直接调用 API 而不使用缓存，所以这个可能性较低。

最可能的原因是 **原因 1**：后端充值接口实现缺陷，缺少余额更新逻辑。

### 修复实现

#### 需要修改的文件

**File**: `backend/api/payments.py` (或对应的后端支付服务文件)

**Function**: `charge()` 或 `POST /api/payments/charge` 的处理函数

#### 具体修改

1. **添加余额更新逻辑**: 在充值成功后（第三方支付网关返回成功或模拟充值成功后），立即查询用户当前余额，计算新余额 = 当前余额 + 充值金额，然后更新数据库中的 `users.available_balance` 字段。

2. **确保事务完整性**: 将充值记录创建和余额更新放在同一个数据库事务中，确保要么全部成功，要么全部回滚，避免数据不一致。

3. **创建交易记录**: 在更新余额的同时，创建一条类型为 `charge` 的交易记录，记录充值金额、时间和状态，便于审计和对账。

4. **返回更新后的余额**: 在充值接口的成功响应中，除了返回 `success=true` 和 `transactionId`，还应返回更新后的 `newBalance`，让客户端可以立即更新本地显示。

5. **添加日志记录**: 在余额更新前后记录日志，包括用户 ID、充值金额、更新前余额、更新后余额，便于排查问题。

---

## Bug 2: 推荐系统日期序列化错误

### Bug 分析

#### 错误信息

```
Object of type date is not JSON serializable
Object of type datetime is not JSON serializable
```

#### 原因

在推荐服务中，使用 `json.dumps()` 和 `json.loads()` 来序列化和反序列化包含 `date` 和 `datetime` 类型的对象，但标准的 JSON 库不知道如何处理这些类型。

### 修复实现

#### 修改文件

1. **backend/app/services/recommendation_service.py**

#### 具体修改

1. **调用模型服务时**: 使用 `request.model_dump_json()` 代替 `json.dumps(request.model_dump())`
   - Pydantic 的 `model_dump_json()` 方法会自动正确处理日期和时间的序列化

2. **缓存推荐时**: 使用 `recommendation.model_dump_json()` 代替 `json.dumps(recommendation.model_dump())`

3. **读取缓存时**: 使用 `RecommendationResponse.model_validate_json(data)` 代替 `RecommendationResponse(**json.loads(data))`
   - Pydantic 的 `model_validate_json()` 方法会自动正确解析 JSON 中的日期和时间字符串

---

## Bug 3: 推荐系统 Redis 缓存错误

### Bug 分析

#### 错误信息

```
'FakeRedis' object has no attribute 'setex'
```

#### 原因

`FakeRedis` 类（用于在没有真实 Redis 时提供兼容接口）缺少 `setex` 方法。

### 修复实现

#### 修改文件

1. **backend/app/redis_client.py**

#### 具体修改

为 `FakeRedis` 类添加 `setex` 方法：

```python
def setex(self, key, time, value):
    self._data[key] = value
    return True
```

---

## Bug 4: 连接超时问题

### Bug 分析

#### 错误信息

```
java.net.SocketTimeoutException: failed to connect to /10.0.2.2 (port 8000)
```

#### 原因

后端服务器配置在端口 9191，但安卓应用连接的是 8000 端口。

### 修复实现

#### 修改文件

1. **backend/run_server.py**

#### 具体修改

将端口从 9191 改回 8000：

```python
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,  # 原来是 9191
    reload=True,
    log_level="info"
)
```

---

## Bug 5: 推荐系统调用时机问题

### Bug 分析

#### 问题

用户点击管家页面时，直接调用推荐 API，导致用户需要等待模型端返回推荐结果。

#### 原因

推荐服务需要时间处理用户数据并返回推荐，但用户在点击管家页面时不应该等待。

### 修复实现

#### 架构修改

1. **推荐只在登录和打卡时调用**
   - 登录成功后，异步调用推荐 API 并缓存结果
   - 打卡成功后，异步调用刷新推荐 API 并更新缓存

2. **管家页面只使用缓存数据**
   - 不直接调用 API
   - 显示"请先登录或打卡后获取推荐"提示（如果没有缓存）

#### 修改文件

1. **android/app/src/main/java/com/weightloss/betting/data/local/RecommendationCacheManager.kt** - 新建
2. **android/app/src/main/java/com/weightloss/betting/data/repository/RecommendationRepository.kt** - 修改
3. **android/app/src/main/java/com/weightloss/betting/ui/main/CoachViewModel.kt** - 修改
4. **android/app/src/main/java/com/weightloss/betting/ui/main/CoachFragment.kt** - 修改
5. **android/app/src/main/res/layout/fragment_coach.xml** - 修改
6. **android/app/src/main/java/com/weightloss/betting/ui/auth/LoginViewModel.kt** - 修改
7. **android/app/src/main/java/com/weightloss/betting/ui/checkin/CheckInViewModel.kt** - 修改
8. **android/app/src/main/java/com/weightloss/betting/di/RepositoryModule.kt** - 修改

---

## 术语表

### Bugfix 术语

- **Bug_Condition (C)**: 充值成功但余额未更新的条件 - 当充值接口返回成功响应但数据库中的用户余额未增加充值金额
- **Property (P)**: 充值成功后的期望行为 - 用户的可用余额应立即增加充值金额,并在数据库中持久化
- **Preservation**: 其他余额操作(冻结、解冻、转账、提现)和余额查询功能必须保持不变
- **charge()**: PaymentRepository 中的充值方法,调用后端 API `/api/payments/charge`
- **getBalance()**: UserRepository 中的获取余额方法,调用后端 API `/api/users/{userId}/balance`
- **availableBalance**: 用户可用余额,可以用于创建赌注计划或提现
- **frozenBalance**: 用户冻结余额,参与活跃计划时被冻结的资金
- **CacheManager**: 本地缓存管理器,缓存用户信息以减少网络请求
