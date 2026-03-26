# 安全审计检查清单

## 1. 认证和授权安全

### 1.1 密码安全
- [ ] 密码使用 bcrypt/Argon2 哈希存储
- [ ] 密码强度要求 (最少8位,包含大小写字母和数字)
- [ ] 实现密码重试限制 (5次失败后锁定账户)
- [ ] 实现密码重置功能 (通过邮箱验证)
- [ ] 密码不在日志中记录
- [ ] 密码不在错误消息中暴露

**测试方法**:
```python
# 检查密码哈希
import bcrypt
password = "Test123456"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
assert bcrypt.checkpw(password.encode(), hashed)

# 检查密码强度验证
weak_passwords = ["123456", "password", "abc123"]
for pwd in weak_passwords:
    response = requests.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": pwd
    })
    assert response.status_code == 400
```

### 1.2 JWT 令牌安全
- [ ] 使用强密钥 (至少256位)
- [ ] 令牌设置合理的过期时间 (访问令牌: 15分钟, 刷新令牌: 7天)
- [ ] 实现令牌刷新机制
- [ ] 令牌签名验证
- [ ] 令牌在 HTTPS 下传输
- [ ] 实现令牌撤销机制 (黑名单)

**测试方法**:
```python
# 检查令牌过期
import jwt
import time

token = jwt.encode(
    {"user_id": "123", "exp": time.time() + 60},
    "secret_key",
    algorithm="HS256"
)

# 等待令牌过期
time.sleep(61)

try:
    jwt.decode(token, "secret_key", algorithms=["HS256"])
    assert False, "令牌应该已过期"
except jwt.ExpiredSignatureError:
    pass  # 正确
```

### 1.3 会话管理
- [ ] 实现会话超时
- [ ] 登出时清除会话
- [ ] 防止会话固定攻击
- [ ] 实现并发会话限制
- [ ] 记录异常登录行为

### 1.4 权限控制
- [ ] 实现基于角色的访问控制 (RBAC)
- [ ] 验证用户只能访问自己的资源
- [ ] 管理员权限分离
- [ ] API 端点权限验证
- [ ] 防止越权访问

**测试方法**:
```python
# 测试越权访问
user1_token = login("user1@example.com", "password")
user2_id = "user2_id"

# 尝试访问其他用户的资源
response = requests.get(
    f"/api/users/{user2_id}",
    headers={"Authorization": f"Bearer {user1_token}"}
)
assert response.status_code == 403  # 应该被拒绝
```

## 2. 数据安全

### 2.1 数据加密
- [ ] 使用 HTTPS/TLS 加密所有通信
- [ ] 敏感数据使用 AES-256 加密存储
- [ ] 数据库连接使用 SSL
- [ ] 备份数据加密
- [ ] 密钥管理安全 (使用密钥管理服务)

**测试方法**:
```bash
# 检查 HTTPS 配置
curl -I https://api.example.com
# 应该返回 200 且使用 TLS 1.2+

# 检查 HTTP 重定向到 HTTPS
curl -I http://api.example.com
# 应该返回 301/302 重定向到 HTTPS
```

### 2.2 数据验证
- [ ] 验证所有输入数据
- [ ] 使用白名单验证
- [ ] 限制输入长度
- [ ] 验证数据类型
- [ ] 验证数据范围

**测试方法**:
```python
# 测试输入验证
invalid_inputs = [
    {"age": -1},  # 负数
    {"age": 200},  # 超出范围
    {"age": "abc"},  # 错误类型
    {"email": "invalid"},  # 无效邮箱
    {"weight": 500},  # 超出范围
]

for data in invalid_inputs:
    response = requests.put("/api/users/123", json=data)
    assert response.status_code == 400
```

### 2.3 数据隐私
- [ ] 实现数据最小化原则
- [ ] 提供数据导出功能
- [ ] 提供数据删除功能
- [ ] 匿名化统计数据
- [ ] 遵循 GDPR/隐私法规
- [ ] 实现数据访问日志

### 2.4 敏感数据处理
- [ ] 不在日志中记录敏感数据
- [ ] 不在错误消息中暴露敏感数据
- [ ] 不在 URL 中传递敏感数据
- [ ] 支付信息不完整存储
- [ ] 实现数据脱敏

## 3. API 安全

### 3.1 SQL 注入防护
- [ ] 使用参数化查询/ORM
- [ ] 验证和转义输入
- [ ] 限制数据库权限
- [ ] 使用最小权限原则

**测试方法**:
```python
# 测试 SQL 注入
malicious_inputs = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1' UNION SELECT * FROM users--",
]

for input_data in malicious_inputs:
    response = requests.get(f"/api/users?search={input_data}")
    # 应该安全处理,不执行恶意 SQL
    assert response.status_code in [200, 400]
```

### 3.2 XSS 防护
- [ ] 转义输出内容
- [ ] 使用 Content-Security-Policy 头
- [ ] 验证和清理用户输入
- [ ] 使用安全的模板引擎

**测试方法**:
```python
# 测试 XSS
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
]

for payload in xss_payloads:
    response = requests.post("/api/comments", json={
        "content": payload
    })
    # 内容应该被转义
    assert "<script>" not in response.text
```

### 3.3 CSRF 防护
- [ ] 实现 CSRF 令牌
- [ ] 验证 Origin/Referer 头
- [ ] 使用 SameSite Cookie 属性
- [ ] 对状态改变操作使用 POST/PUT/DELETE

**测试方法**:
```python
# 测试 CSRF 保护
response = requests.post("/api/betting-plans", json={
    "bet_amount": 100
})
# 没有 CSRF 令牌应该被拒绝
assert response.status_code == 403
```

### 3.4 请求限流
- [ ] 实现 API 限流 (每分钟100请求)
- [ ] 实现登录限流 (每分钟5次)
- [ ] 实现 IP 限流
- [ ] 返回 429 状态码
- [ ] 提供 Retry-After 头

**测试方法**:
```python
# 测试限流
for i in range(150):
    response = requests.get("/api/users/123")
    if i >= 100:
        assert response.status_code == 429
```

### 3.5 输入验证
- [ ] 验证所有 API 输入
- [ ] 使用 JSON Schema 验证
- [ ] 限制请求大小
- [ ] 验证文件上传类型和大小
- [ ] 防止路径遍历攻击

## 4. 支付安全

### 4.1 支付数据安全
- [ ] 遵循 PCI DSS 标准
- [ ] 不存储完整信用卡号
- [ ] 使用支付令牌化
- [ ] 验证支付回调签名
- [ ] 实现幂等性防止重复支付

**测试方法**:
```python
# 测试支付回调验证
invalid_signature = "invalid_signature"
response = requests.post("/api/payments/webhook", 
    json={"amount": 100},
    headers={"Signature": invalid_signature}
)
assert response.status_code == 401  # 应该拒绝无效签名
```

### 4.2 资金安全
- [ ] 实现资金冻结机制
- [ ] 验证余额充足
- [ ] 使用数据库事务
- [ ] 实现资金守恒验证
- [ ] 记录所有资金操作
- [ ] 实现争议处理机制

### 4.3 支付欺诈防护
- [ ] 实现风控规则
- [ ] 检测异常交易
- [ ] 实现交易限额
- [ ] 验证用户身份
- [ ] 记录可疑行为

## 5. 基础设施安全

### 5.1 服务器安全
- [ ] 使用最新的操作系统和软件
- [ ] 关闭不必要的端口和服务
- [ ] 配置防火墙
- [ ] 实现入侵检测
- [ ] 定期安全更新

### 5.2 数据库安全
- [ ] 使用强密码
- [ ] 限制数据库访问
- [ ] 启用审计日志
- [ ] 定期备份
- [ ] 加密备份数据

### 5.3 网络安全
- [ ] 使用 VPN/专用网络
- [ ] 实现 DDoS 防护
- [ ] 使用 CDN
- [ ] 配置 WAF (Web Application Firewall)
- [ ] 实现负载均衡

## 6. 日志和监控

### 6.1 安全日志
- [ ] 记录所有认证尝试
- [ ] 记录权限变更
- [ ] 记录敏感操作
- [ ] 记录异常行为
- [ ] 日志不包含敏感数据

### 6.2 监控告警
- [ ] 监控异常登录
- [ ] 监控 API 异常
- [ ] 监控资金异常
- [ ] 实现实时告警
- [ ] 定期审查日志

## 7. 移动端安全

### 7.1 Android 安全
- [ ] 启用代码混淆 (ProGuard/R8)
- [ ] 使用 SafetyNet API
- [ ] 实现证书固定
- [ ] 安全存储敏感数据 (EncryptedSharedPreferences)
- [ ] 防止截屏 (支付页面)
- [ ] 检测 Root 设备

### 7.2 iOS 安全
- [ ] 启用代码混淆
- [ ] 使用 Keychain 存储敏感数据
- [ ] 实现证书固定
- [ ] 使用 App Transport Security
- [ ] 防止截屏 (支付页面)
- [ ] 检测越狱设备

## 8. 第三方依赖安全

### 8.1 依赖管理
- [ ] 定期更新依赖
- [ ] 扫描已知漏洞
- [ ] 使用可信的依赖源
- [ ] 锁定依赖版本
- [ ] 审查依赖许可证

**工具**:
```bash
# Python
pip install safety
safety check

# Node.js
npm audit
npm audit fix

# Android
./gradlew dependencyCheckAnalyze

# iOS
pod outdated
```

## 9. 安全测试

### 9.1 自动化安全扫描
- [ ] 使用 OWASP ZAP 扫描
- [ ] 使用 Burp Suite 测试
- [ ] 使用 SonarQube 代码分析
- [ ] 使用 Snyk 依赖扫描

### 9.2 渗透测试
- [ ] 进行定期渗透测试
- [ ] 测试常见攻击场景
- [ ] 测试业务逻辑漏洞
- [ ] 生成渗透测试报告

## 10. 应急响应

### 10.1 安全事件响应
- [ ] 制定应急响应计划
- [ ] 建立安全团队
- [ ] 定义事件等级
- [ ] 实现快速回滚机制
- [ ] 准备通知模板

### 10.2 漏洞修复流程
- [ ] 建立漏洞报告渠道
- [ ] 定义修复优先级
- [ ] 实现快速修复流程
- [ ] 验证修复效果
- [ ] 发布安全公告

## 安全审计报告模板

### 安全审计报告

**审计日期**: YYYY-MM-DD  
**审计范围**: 
- 后端 API
- Android 客户端
- iOS 客户端
- 基础设施

**审计结果**:

| 类别 | 检查项 | 状态 | 风险等级 | 备注 |
|------|--------|------|----------|------|
| 认证 | 密码哈希 | ✅/❌ | 高/中/低 | |
| 认证 | JWT 安全 | ✅/❌ | 高/中/低 | |
| 数据 | 加密传输 | ✅/❌ | 高/中/低 | |
| API | SQL 注入防护 | ✅/❌ | 高/中/低 | |
| API | XSS 防护 | ✅/❌ | 高/中/低 | |
| 支付 | PCI DSS 合规 | ✅/❌ | 高/中/低 | |

**发现的安全问题**:

1. **[高危] 问题标题**
   - 描述: [详细描述]
   - 影响: [影响范围]
   - 建议: [修复建议]
   - 状态: 待修复/已修复

2. **[中危] 问题标题**
   - 描述: [详细描述]
   - 影响: [影响范围]
   - 建议: [修复建议]
   - 状态: 待修复/已修复

**安全评分**: XX/100

**总体评估**:
[安全状况总结]

**改进建议**:
1. [建议1]
2. [建议2]

**下次审计时间**: YYYY-MM-DD
