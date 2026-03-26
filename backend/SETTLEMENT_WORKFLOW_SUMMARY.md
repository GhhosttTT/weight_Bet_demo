# 结算流程实现总结

## 正确的结算流程

根据用户需求，结算流程应该是：

```
打开 App → 调用检查接口 → 发现到结算日 → 弹出结算弹窗 
→ 点击确认结算 → 进入计划详情 → 开始结算流程
```

## 已实现的功能

### 1. 结算日检查接口 ✅

**API:** `GET /api/settlement-check`

**功能:** 
- App 启动时调用此接口
- 返回所有已到期的 active 状态计划
- 包含每个计划的结算状态信息

**响应格式:**
```json
[
  {
    "plan_id": "abc123",
    "description": "减肥计划描述",
    "end_date": "2026-03-24T00:00:00",
    "bet_amount": 100.0,
    "has_settlement": false,
    "in_progress": false
  }
]
```

**字段说明:**
- `has_settlement`: 是否已有结算记录
- `in_progress`: 结算选择流程是否正在进行中

### 2. 提交结算选择 ✅

**API:** `POST /api/settlement-choices/{plan_id}`

**请求体:**
```json
{
  "self_achieved": true,
  "opponent_achieved": false
}
```

**功能:**
- 用户在选择轮次内提交自己的选择
- 支持三轮选择机制
- 24 小时超时自动推进

### 3. 查询选择状态 ✅

**API:** `GET /api/settlement-choices/{plan_id}/status`

**功能:**
- 查看当前轮次
- 查看双方是否已提交
- 查看匹配状态

### 4. 匹配双方选择 ✅

**API:** `POST /api/settlement-choices/{plan_id}/match`

**匹配规则:**
1. **双方都选"都达成"** → 原路返还，无手续费
2. **双方都选"都未达成"** → 扣 10% 后平分
3. **一方选"我成对方败"+另一方选"我败对方成"** → 前者获胜，获得全部
4. **不匹配** → 进入下一轮（最多 3 轮）
5. **三次不匹配** → 强制仲裁（扣 15% 仲裁费）

### 5. 超时处理 ✅

**API:** `POST /api/settlement-choices/{plan_id}/check-timeout`

**功能:**
- 检查是否有用户超时（默认 24 小时）
- 自动推进到下一轮
- 记录超时信息

### 6. 执行结算 ✅

**API:** `POST /api/settlements/execute/{plan_id}`

**功能:**
- 基于匹配结果执行最终结算
- 解冻双方资金
- 转账给获胜方
- 更新计划状态为 COMPLETED
- 创建结算记录

### 7. 定时任务脚本 ✅

**文件:** `backend/scripts/check_settlement_deadline.py`

**功能:**
- 定期扫描到期计划
- 标记过期计划
- 记录需要结算的计划信息

**配置建议 (crontab):**
```bash
# 每小时执行一次
0 * * * * cd /path/to/backend && python scripts/check_settlement_deadline.py
```

## 完整的业务流程

### 阶段 1: 计划到期检测
```
1. 定时任务每小时运行 check_settlement_deadline.py
2. 扫描所有 active 状态且 end_date <= now 的计划
3. 将计划状态标记为 EXPIRED
4. 发送推送通知提醒用户
```

### 阶段 2: App 端检测和弹窗
```
1. 用户打开 App
2. App 调用 GET /api/settlement-check
3. 如果有到期计划，显示弹窗提示
4. 用户点击"去结算"按钮
```

### 阶段 3: 结算选择流程
```
1. 进入计划详情页
2. 显示结算选择界面
3. 用户提交选择 (自达成 + 对方达成情况)
4. 等待对方也提交选择
```

### 阶段 4: 系统匹配和结算
```
1. 双方都提交后，系统自动匹配
2. 如果匹配成功 → 直接结算
3. 如果不匹配 → 进入下一轮（最多 3 轮）
4. 超时 → 自动推进到下一轮
5. 3 轮不匹配 → 强制仲裁
```

## 数据模型

### SettlementChoice 表
```sql
CREATE TABLE settlement_choices (
    id VARCHAR(36) PRIMARY KEY,
    plan_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    self_achieved BOOLEAN NOT NULL,
    opponent_achieved BOOLEAN NOT NULL,
    round INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES betting_plans(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Settlement 表
```sql
CREATE TABLE settlements (
    id VARCHAR(36) PRIMARY KEY,
    plan_id VARCHAR(36) UNIQUE NOT NULL,
    creator_achieved BOOLEAN NOT NULL,
    participant_achieved BOOLEAN NOT NULL,
    creator_final_weight FLOAT NOT NULL,
    participant_final_weight FLOAT NOT NULL,
    creator_weight_loss FLOAT NOT NULL,
    participant_weight_loss FLOAT NOT NULL,
    creator_amount FLOAT NOT NULL,
    participant_amount FLOAT NOT NULL,
    platform_fee FLOAT NOT NULL,
    in_arbitration BOOLEAN DEFAULT FALSE,
    arbitration_fee FLOAT,
    settlement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES betting_plans(id)
);
```

## 单元测试覆盖

### 已通过测试 (17/17) ✅

**test_settlement_choice_service.py:**
- ✅ TestSubmitChoice (5 个测试)
  - 成功提交选择
  - 计划不存在
  - 未授权用户
  - 已完成计划
  - 重复提交
  
- ✅ TestMatchChoices (6 个测试)
  - 双方都达成
  - 创建者获胜
  - 参与者获胜
  - 第一轮不匹配
  - 三轮不匹配仲裁
  - 等待双方提交
  
- ✅ TestGetSelectionStatus (2 个测试)
- ✅ TestCheckTimeoutAndAdvance (4 个测试)
  - 超时自动推进
  - 双方都已提交

## API 使用示例

### 1. App 启动检查结算日
```python
import requests

# App 启动时调用
response = requests.get(
    "http://localhost:8000/api/settlement-check",
    headers={"Authorization": f"Bearer {token}"}
)

expired_plans = response.json()
for plan in expired_plans:
    if not plan["has_settlement"] and not plan["in_progress"]:
        # 显示弹窗提示用户去结算
        show_settlement_popup(plan)
```

### 2. 提交结算选择
```python
# 用户 A 选择：我达成，对方未达成
choice_response = requests.post(
    "http://localhost:8000/api/settlement-choices/plan123",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "self_achieved": True,
        "opponent_achieved": False
    }
)
```

### 3. 查询选择状态
```python
# 查看双方是否都提交了选择
status = requests.get(
    "http://localhost:8000/api/settlement-choices/plan123/status",
    headers={"Authorization": f"Bearer {token}"}
).json()

if status["creator_submitted"] and status["participant_submitted"]:
    print("双方都已提交，等待系统匹配...")
```

### 4. 触发匹配（通常由后端自动调用）
```python
# 后端定时任务调用
match_result = requests.post(
    "http://localhost:8000/api/settlement-choices/plan123/match",
    headers={"Authorization": f"Bearer {admin_token}"}
).json()

if match_result["matched"]:
    print(f"匹配成功！创建者获胜：{match_result['creator_won']}")
    # 自动执行结算
    settlement = requests.post(
        "http://localhost:8000/api/settlements/execute/plan123",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
```

## 注意事项

### 1. 支付冻结依赖
执行结算时需要解冻资金，测试环境中需要预先创建冻结交易记录。

### 2. 认证机制
匹配和超时检查接口应该由定时任务或管理员调用，需要添加 API Key 认证。

### 3. 超时时间
- 每轮选择超时：24 小时（可配置）
- 建议在前端显示倒计时

### 4. 仲裁机制
三次不匹配后自动进入仲裁：
- 扣除 15% 作为仲裁费
- 根据实际打卡数据判定胜负
- 由系统自动执行

## 待优化事项

1. **实际转账逻辑**: 目前 execute_settlement 中的转账是 TODO 状态
2. **通知推送**: 结算完成后应发送推送通知
3. **API 认证**: match_choices 和 check_timeout 需要添加 API Key 认证
4. **前端集成**: 需要在移动端实现对应的 UI 界面
5. **定时任务部署**: 配置生产环境的 cron job

## 相关文件

### 后端 API
- `backend/app/api/settlement_choices.py` - 结算选择路由
- `backend/app/api/settlements.py` - 结算路由
- `backend/app/schemas/settlement_choice.py` - Schema 定义
- `backend/app/models/settlement_choice.py` - 数据模型

### 服务层
- `backend/app/services/settlement_choice_service.py` - 选择服务
- `backend/app/services/settlement_service.py` - 结算服务
- `backend/app/services/arbitration_service.py` - 仲裁服务

### 定时任务
- `backend/scripts/check_settlement_deadline.py` - 结算日检查脚本

### 测试
- `backend/tests/test_settlement_choice_service.py` - 服务层单元测试（17 个通过）
- `backend/tests/test_settlement_workflow.py` - 完整流程集成测试
