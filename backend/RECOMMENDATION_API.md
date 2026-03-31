# 推荐功能 API 对接文档

## 概述
本文档描述了减肥对赌 APP 后端与推荐模型侧的 API 对接方式。

## 网络配置

### 后端地址
当前后端部署在：
- **局域网地址**: `http://192.168.1.10:9191`
- **本地地址**: `http://localhost:9191`

### 模型侧地址
后端配置的模型侧地址（已在 `app/config.py` 中设置）:
- **地址**: `http://192.168.1.108:8000`

---

## API 接口

### 1. 模型侧提供的接口（后端调用模型侧）

#### POST /api/recommend
模型侧需要提供此接口，用于接收用户数据并返回推荐结果。

**请求地址**: `POST http://192.168.1.108:8000/api/recommend`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "user_profile": {
    "user_id": "用户ID",
    "age": 25,
    "gender": "male",
    "height": 175.0,
    "current_weight": 70.0,
    "target_weight": 65.0,
    "initial_weight": 75.0
  },
  "check_in_records": [
    {
      "check_in_date": "2026-03-30",
      "weight": 69.5,
      "note": "今天运动了"
    }
  ],
  "request_type": "login"
}
```

**字段说明**:
- `user_profile.user_id`: 用户唯一标识
- `user_profile.age`: 年龄
- `user_profile.gender`: 性别（male/female/other）
- `user_profile.height`: 身高（cm）
- `user_profile.current_weight`: 当前体重（kg）
- `user_profile.target_weight`: 目标体重（kg，可选）
- `user_profile.initial_weight`: 初始体重（kg，可选）
- `check_in_records`: 最近的打卡记录（最多30条）
- `request_type`: 请求类型（"login" 登录时调用，"check_in" 打卡后调用）

**响应**:
```json
{
  "success": true,
  "exercise_recommendations": [
    {
      "type": "跑步",
      "duration": 30,
      "intensity": "medium",
      "description": "建议慢跑30分钟"
    }
  ],
  "diet_recommendations": [
    {
      "meal_type": "breakfast",
      "food_items": ["燕麦", "鸡蛋", "牛奶"],
      "calories": 350,
      "tips": "早餐要吃好"
    }
  ],
  "daily_calories_target": 1800,
  "water_intake_target": 2000,
  "sleep_target": 8,
  "tips": "综合建议",
  "generated_at": "2026-03-31T10:00:00"
}
```

**字段说明**:
- `success`: 是否成功
- `exercise_recommendations`: 运动推荐列表
- `diet_recommendations`: 饮食推荐列表
- `daily_calories_target`: 每日热量目标（千卡，可选）
- `water_intake_target`: 每日饮水目标（ml，可选）
- `sleep_target`: 每日睡眠目标（小时，可选）
- `tips`: 综合建议（可选）
- `generated_at`: 推荐生成时间

---

### 2. 后端提供的接口（仅内部使用）

#### GET /api/recommendations/
获取推荐（登录时调用）

**请求地址**: `GET http://{后端地址}/api/recommendations/`

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `use_cache`: 是否使用缓存（默认 true）

#### POST /api/recommendations/refresh
刷新推荐（打卡后调用）

**请求地址**: `POST http://{后端地址}/api/recommendations/refresh`

**请求头**:
```
Authorization: Bearer <access_token>
```

---

## 调用流程

### 场景1：用户登录时
1. 用户登录成功
2. 前端调用 `GET /api/recommendations/`
3. 后端检查缓存，如有则直接返回
4. 后端从数据库获取用户资料和打卡记录
5. 后端调用模型侧 `POST /api/recommend`
6. 后端缓存结果并返回给前端

### 场景2：用户打卡后
1. 用户完成打卡
2. 前端调用 `POST /api/recommendations/refresh`
3. 后端不使用缓存，直接获取最新数据
4. 后端调用模型侧 `POST /api/recommend`
5. 后端更新缓存并返回最新推荐

---

## 注意事项

1. **超时设置**: 后端调用模型侧的超时时间为 30 秒
2. **缓存策略**: 推荐结果默认缓存 1 小时
3. **错误处理**: 模型侧返回非 200 状态码时，后端会返回 503 错误
4. **网络连通性**: 请确保后端能够访问到模型侧的地址 `192.168.1.108:8000`

---

## 测试

可以使用以下命令测试模型侧接口是否正常：

```bash
curl -X POST http://192.168.1.108:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "user_id": "test-user",
      "age": 25,
      "gender": "male",
      "height": 175.0,
      "current_weight": 70.0
    },
    "check_in_records": [],
    "request_type": "login"
  }'
```
