# 充值后余额未更新 Bugfix Design

## Overview

用户在充值成功后立即创建赌注计划时,系统仍然报告余额不足。这个bug的核心问题是:充值接口虽然返回成功响应,但用户的账户余额并未在数据库中更新。当用户随后尝试创建需要资金的赌注计划时,系统检查余额时仍然读取到充值前的旧余额(0.0元),导致余额不足错误。

修复策略是确保充值成功后,系统立即在数据库中持久化更新用户的可用余额,并且在客户端侧清除可能存在的余额缓存,确保后续操作能获取到最新的余额数据。

## Glossary

- **Bug_Condition (C)**: 充值成功但余额未更新的条件 - 当充值接口返回成功响应但数据库中的用户余额未增加充值金额
- **Property (P)**: 充值成功后的期望行为 - 用户的可用余额应立即增加充值金额,并在数据库中持久化
- **Preservation**: 其他余额操作(冻结、解冻、转账、提现)和余额查询功能必须保持不变
- **charge()**: PaymentRepository 中的充值方法,调用后端 API `/api/payments/charge`
- **getBalance()**: UserRepository 中的获取余额方法,调用后端 API `/api/users/{userId}/balance`
- **availableBalance**: 用户可用余额,可以用于创建赌注计划或提现
- **frozenBalance**: 用户冻结余额,参与活跃计划时被冻结的资金
- **CacheManager**: 本地缓存管理器,缓存用户信息以减少网络请求

## Bug Details

### Bug Condition

该bug在用户充值成功后立即尝试使用充值金额时触发。充值接口 `/api/payments/charge` 返回成功响应 `{"success":true,"message":"充值成功","amount":200.0}`,但后端未在数据库中更新用户的 `availableBalance` 字段。当用户随后创建赌注计划时,系统调用 `getBalance()` 查询余额,仍然读取到充值前的旧值。

**Formal Specification:**
```
FUNCTION isBugCondition(chargeResult, subsequentBalanceQuery)
  INPUT: chargeResult of type ChargeResult, subsequentBalanceQuery of type Balance
  OUTPUT: boolean
  
  RETURN chargeResult.success = true
         AND chargeResult.amount > 0
         AND subsequentBalanceQuery.availableBalance = previousBalance
         AND subsequentBalanceQuery.availableBalance < (previousBalance + chargeResult.amount)
END FUNCTION
```

### Examples

- **示例 1**: 用户余额为 0.0 元,充值 200.0 元成功(接口返回 `{"success":true,"amount":200.0}`),立即查询余额仍为 0.0 元,创建 200 元赌注计划时报错"余额不足,需要充值 200.0 元"
- **示例 2**: 用户余额为 50.0 元,充值 100.0 元成功,立即查询余额仍为 50.0 元,创建 150 元赌注计划时报错"余额不足,需要充值 100.0 元"
- **示例 3**: 用户余额为 0.0 元,充值 500.0 元成功,等待 5 分钟后查询余额仍为 0.0 元(说明不是延迟问题,而是根本没有更新)
- **边缘情况**: 用户充值 1.0 元(最小金额),充值成功后余额应为 previousBalance + 1.0,但实际仍为 previousBalance

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- 用户余额充足时创建赌注计划,系统必须继续成功冻结赌金并创建计划
- 用户余额不足且未充值时创建赌注计划,系统必须继续返回余额不足错误
- 充值失败(充值接口返回 `success=false`)时,系统必须继续不更新用户余额
- 用户查询账户余额时,系统必须继续返回准确的可用余额和冻结余额
- 系统执行结算转账操作时,必须继续正确更新用户余额
- 用户提现操作时,必须继续正确扣减用户可用余额
- 冻结资金操作(创建/接受计划)时,必须继续正确减少可用余额并增加冻结余额
- 解冻资金操作(取消计划/结算)时,必须继续正确减少冻结余额并增加可用余额

**Scope:**
所有不涉及充值成功场景的余额操作都应完全不受此修复影响。这包括:
- 余额查询操作
- 冻结/解冻资金操作
- 转账操作
- 提现操作
- 充值失败场景

## Hypothesized Root Cause

基于bug描述和代码分析,最可能的根本原因是:

1. **后端充值接口实现缺陷**: `/api/payments/charge` 接口在处理充值请求时,可能只是创建了充值订单记录或调用了第三方支付网关,但没有在数据库中更新用户的 `availableBalance` 字段。接口返回成功响应,但实际的余额更新逻辑缺失或未执行。

2. **数据库事务未提交**: 后端可能在事务中更新了余额,但由于某种原因(异常、事务回滚、未显式提交)导致更新未持久化到数据库。

3. **异步处理问题**: 后端可能将余额更新放在异步任务中处理,但异步任务执行失败或延迟过长,导致用户立即查询时看不到更新。

4. **缓存不一致**: 虽然数据库已更新,但客户端或服务端的缓存层未刷新,导致查询时返回旧的缓存数据。但根据代码分析,`getBalance()` 方法直接调用 API 而不使用缓存,所以这个可能性较低。

最可能的原因是 **原因 1**:后端充值接口实现缺陷,缺少余额更新逻辑。

## Correctness Properties

Property 1: Bug Condition - 充值成功后余额立即更新

_For any_ 充值请求,当充值接口返回成功响应(`success=true`)时,系统 SHALL 立即在数据库中将用户的 `availableBalance` 增加充值金额,并且后续的余额查询 SHALL 返回更新后的余额值。

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - 非充值成功场景的余额操作行为

_For any_ 余额操作,如果不是充值成功场景(包括充值失败、余额查询、冻结/解冻、转账、提现),系统 SHALL 产生与原始代码完全相同的行为,保持所有现有余额操作的正确性。

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

## Fix Implementation

### Changes Required

假设我们的根本原因分析正确(后端充值接口缺少余额更新逻辑),需要进行以下修改:

**File**: `backend/api/payments.py` (或对应的后端支付服务文件)

**Function**: `charge()` 或 `POST /api/payments/charge` 的处理函数

**Specific Changes**:
1. **添加余额更新逻辑**: 在充值成功后(第三方支付网关返回成功或模拟充值成功后),立即查询用户当前余额,计算新余额 = 当前余额 + 充值金额,然后更新数据库中的 `users.available_balance` 字段。

2. **确保事务完整性**: 将充值记录创建和余额更新放在同一个数据库事务中,确保要么全部成功,要么全部回滚,避免数据不一致。

3. **创建交易记录**: 在更新余额的同时,创建一条类型为 `charge` 的交易记录,记录充值金额、时间和状态,便于审计和对账。

4. **返回更新后的余额**: 在充值接口的成功响应中,除了返回 `success=true` 和 `transactionId`,还应返回更新后的 `newBalance`,让客户端可以立即更新本地显示。

5. **添加日志记录**: 在余额更新前后记录日志,包括用户ID、充值金额、更新前余额、更新后余额,便于排查问题。

**伪代码示例**:
```python
def charge(user_id, amount, payment_method_id):
    # 验证参数
    if amount <= 0:
        return {"success": False, "message": "充值金额必须大于0"}
    
    # 开始数据库事务
    with database.transaction():
        # 1. 调用第三方支付网关(或模拟充值)
        payment_result = payment_gateway.process_charge(amount, payment_method_id)
        
        if not payment_result.success:
            return {"success": False, "message": "支付处理失败"}
        
        # 2. 查询用户当前余额
        user = database.query("SELECT * FROM users WHERE id = ?", user_id)
        old_balance = user.available_balance
        
        # 3. 计算新余额
        new_balance = old_balance + amount
        
        # 4. 更新用户余额 (关键修复点)
        database.execute(
            "UPDATE users SET available_balance = ? WHERE id = ?",
            new_balance, user_id
        )
        
        # 5. 创建交易记录
        transaction_id = generate_uuid()
        database.execute(
            "INSERT INTO transactions (id, user_id, type, amount, status, created_at) VALUES (?, ?, 'charge', ?, 'completed', NOW())",
            transaction_id, user_id, amount
        )
        
        # 6. 记录日志
        log.info(f"User {user_id} charged {amount}, balance updated from {old_balance} to {new_balance}")
        
        # 7. 提交事务
        database.commit()
    
    # 8. 返回成功响应,包含新余额
    return {
        "success": True,
        "transactionId": transaction_id,
        "message": "充值成功",
        "amount": amount,
        "newBalance": new_balance
    }
```

### Client-Side Changes (Optional but Recommended)

**File**: `android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt`

**Function**: `createCharge()`

**Specific Changes**:
1. **清除余额缓存**: 充值成功后,调用 `UserRepository.clearCache()` 或 `CacheManager.clearUserCache()` 清除本地缓存的用户信息,确保下次查询余额时从服务器获取最新数据。

2. **主动刷新余额**: 充值成功后,主动调用 `UserRepository.getBalance(userId, forceRefresh=true)` 强制从服务器刷新余额,并更新本地缓存。

## Testing Strategy

### Validation Approach

测试策略遵循两阶段方法:首先,在未修复的代码上运行探索性测试,验证bug确实存在并理解其表现;然后,在修复后的代码上运行修复检查和保留检查,验证bug已修复且未引入回归。

### Exploratory Bug Condition Checking

**Goal**: 在实施修复之前,在未修复的代码上运行测试,验证bug确实存在。确认或反驳根本原因分析。如果反驳,需要重新假设根本原因。

**Test Plan**: 编写测试用例模拟用户充值流程,在充值成功后立即查询余额,断言余额未更新(在未修复代码上应该失败,证明bug存在)。同时检查数据库中的 `users.available_balance` 字段,确认是数据库未更新还是查询缓存问题。

**Test Cases**:
1. **基本充值测试**: 用户余额为 0.0 元,充值 200.0 元,充值接口返回成功,立即查询余额,断言余额仍为 0.0 元(在未修复代码上会通过,证明bug存在)
2. **增量充值测试**: 用户余额为 50.0 元,充值 100.0 元,充值接口返回成功,立即查询余额,断言余额仍为 50.0 元而不是 150.0 元(在未修复代码上会通过)
3. **数据库直接查询测试**: 充值成功后,直接查询数据库 `SELECT available_balance FROM users WHERE id = ?`,断言数据库中的值未更新(确认是数据库问题而非缓存问题)
4. **延迟查询测试**: 充值成功后等待 10 秒再查询余额,断言余额仍未更新(排除异步延迟问题)

**Expected Counterexamples**:
- 充值接口返回 `{"success":true,"amount":200.0}`,但数据库中 `users.available_balance` 未增加 200.0
- 后续余额查询返回充值前的旧余额
- 可能原因:后端充值接口缺少余额更新逻辑,或事务未提交,或异步任务失败

### Fix Checking

**Goal**: 验证对于所有充值成功的场景,修复后的代码能正确更新用户余额。

**Pseudocode:**
```
FOR ALL chargeRequest WHERE chargeRequest.amount > 0 DO
  oldBalance := getBalance(userId)
  chargeResult := charge_fixed(userId, chargeRequest)
  
  IF chargeResult.success = true THEN
    newBalance := getBalance(userId)
    ASSERT newBalance = oldBalance + chargeRequest.amount
    
    // 验证数据库已持久化
    dbBalance := queryDatabase("SELECT available_balance FROM users WHERE id = ?", userId)
    ASSERT dbBalance = newBalance
    
    // 验证交易记录已创建
    transaction := queryDatabase("SELECT * FROM transactions WHERE id = ?", chargeResult.transactionId)
    ASSERT transaction.type = "charge"
    ASSERT transaction.amount = chargeRequest.amount
    ASSERT transaction.status = "completed"
  END IF
END FOR
```

**Test Cases**:
1. **基本充值修复验证**: 用户余额为 0.0 元,充值 200.0 元,验证余额更新为 200.0 元
2. **增量充值修复验证**: 用户余额为 50.0 元,充值 100.0 元,验证余额更新为 150.0 元
3. **最小金额充值**: 用户余额为 0.0 元,充值 1.0 元,验证余额更新为 1.0 元
4. **大额充值**: 用户余额为 0.0 元,充值 10000.0 元,验证余额更新为 10000.0 元
5. **多次连续充值**: 用户余额为 0.0 元,连续充值 100.0 元三次,验证余额最终为 300.0 元
6. **充值后立即创建计划**: 用户余额为 0.0 元,充值 200.0 元,立即创建 200 元赌注计划,验证计划创建成功且余额冻结正确

### Preservation Checking

**Goal**: 验证对于所有非充值成功的场景,修复后的代码产生与原始代码完全相同的行为。

**Pseudocode:**
```
FOR ALL operation WHERE NOT isChargeSuccessOperation(operation) DO
  ASSERT behavior_original(operation) = behavior_fixed(operation)
END FOR
```

**Testing Approach**: 基于属性的测试(Property-Based Testing)推荐用于保留检查,因为:
- 它自动生成大量测试用例覆盖输入域
- 它能捕获手动单元测试可能遗漏的边缘情况
- 它提供强有力的保证,确保所有非bug场景的行为保持不变

**Test Plan**: 首先在未修复代码上观察各种余额操作的行为,记录预期结果,然后编写基于属性的测试捕获这些行为,在修复后的代码上运行,验证行为一致。

**Test Cases**:
1. **充值失败保留**: 观察未修复代码上充值失败(amount <= 0 或支付网关返回失败)时余额不变,编写测试验证修复后行为相同
2. **余额查询保留**: 观察未修复代码上余额查询返回准确的可用余额和冻结余额,编写测试验证修复后查询结果相同
3. **冻结资金保留**: 观察未修复代码上创建计划时冻结资金的行为(可用余额减少,冻结余额增加),编写测试验证修复后行为相同
4. **解冻资金保留**: 观察未修复代码上取消计划时解冻资金的行为(冻结余额减少,可用余额增加),编写测试验证修复后行为相同
5. **转账操作保留**: 观察未修复代码上结算转账时的余额变化,编写测试验证修复后行为相同
6. **提现操作保留**: 观察未修复代码上提现时的余额扣减,编写测试验证修复后行为相同
7. **余额不足错误保留**: 观察未修复代码上余额不足时创建计划的错误响应,编写测试验证修复后错误响应相同

### Unit Tests

- 测试充值成功后余额更新的基本场景(零余额充值、有余额增量充值)
- 测试充值失败场景(金额无效、支付网关失败)余额不变
- 测试充值成功后交易记录正确创建
- 测试充值操作的事务完整性(模拟数据库异常,验证回滚)
- 测试边缘情况(最小金额、最大金额、多次连续充值)

### Property-Based Tests

- 生成随机的充值金额和初始余额,验证充值成功后余额 = 初始余额 + 充值金额
- 生成随机的余额操作序列(充值、冻结、解冻、转账、提现),验证最终余额计算正确
- 生成随机的充值失败场景,验证余额保持不变
- 测试并发充值场景,验证余额更新的原子性和一致性

### Integration Tests

- 测试完整的充值到创建计划流程:用户余额不足 -> 充值 -> 创建计划 -> 验证计划创建成功且余额冻结正确
- 测试充值后的余额查询:充值成功 -> 查询余额 -> 验证返回最新余额
- 测试充值后的提现:充值成功 -> 提现 -> 验证余额正确扣减
- 测试多用户并发充值场景,验证系统稳定性和数据一致性
