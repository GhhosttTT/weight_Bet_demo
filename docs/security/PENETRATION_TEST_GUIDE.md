# 渗透测试指南

## 测试范围

本渗透测试针对减肥对赌 APP 的以下组件:
- 后端 API (http://localhost:8000)
- Android 客户端
- iOS 客户端
- 数据库和缓存

## 测试方法

### 1. 信息收集

#### 1.1 端口扫描
```bash
# 使用 nmap 扫描开放端口
nmap -sV -p- localhost

# 预期结果:
# 8000/tcp open  http
# 5432/tcp open  postgresql
# 6379/tcp open  redis
```

#### 1.2 目录枚举
```bash
# 使用 dirb 枚举目录
dirb http://localhost:8000 /usr/share/wordlists/dirb/common.txt

# 使用 gobuster
gobuster dir -u http://localhost:8000 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

#### 1.3 API 端点发现
```bash
# 查看 API 文档
curl http://localhost:8000/docs
curl http://localhost:8000/openapi.json

# 枚举 API 端点
ffuf -w api-endpoints.txt -u http://localhost:8000/api/FUZZ
```

### 2. 认证和授权测试

#### 2.1 弱密码测试
```python
import requests

# 常见弱密码列表
weak_passwords = [
    "123456", "password", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon"
]

for password in weak_passwords:
    response = requests.post("http://localhost:8000/api/auth/register", json={
        "email": "test@example.com",
        "password": password,
        "nickname": "Test"
    })
    if response.status_code == 201:
        print(f"弱密码被接受: {password}")
```

#### 2.2 暴力破解测试
```bash
# 使用 hydra 进行暴力破解
hydra -l admin@example.com -P /usr/share/wordlists/rockyou.txt \
      localhost http-post-form "/api/auth/login:email=^USER^&password=^PASS^:F=Invalid"

# 应该被限流阻止
```

#### 2.3 JWT 令牌测试
```python
import jwt
import requests

# 测试弱密钥
weak_keys = ["secret", "123456", "password"]
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

for key in weak_keys:
    try:
        decoded = jwt.decode(token, key, algorithms=["HS256"])
        print(f"弱密钥发现: {key}")
    except:
        pass

# 测试令牌篡改
payload = jwt.decode(token, options={"verify_signature": False})
payload["user_id"] = "admin"
forged_token = jwt.encode(payload, "secret", algorithm="HS256")

response = requests.get("http://localhost:8000/api/users/admin",
    headers={"Authorization": f"Bearer {forged_token}"})
# 应该被拒绝
```

#### 2.4 会话固定测试
```python
# 1. 获取会话令牌
response1 = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})
token1 = response1.json()["access_token"]

# 2. 登出
requests.post("http://localhost:8000/api/auth/logout",
    headers={"Authorization": f"Bearer {token1}"})

# 3. 尝试使用旧令牌
response2 = requests.get("http://localhost:8000/api/users/123",
    headers={"Authorization": f"Bearer {token1}"})

# 应该返回 401
assert response2.status_code == 401
```

#### 2.5 越权访问测试
```python
# 用户 A 的令牌
token_a = login("userA@example.com", "password")

# 尝试访问用户 B 的资源
response = requests.get("http://localhost:8000/api/users/userB_id",
    headers={"Authorization": f"Bearer {token_a}"})

# 应该返回 403
assert response.status_code == 403

# 尝试修改用户 B 的数据
response = requests.put("http://localhost:8000/api/users/userB_id",
    headers={"Authorization": f"Bearer {token_a}"},
    json={"nickname": "Hacked"})

# 应该返回 403
assert response.status_code == 403
```

### 3. 注入攻击测试

#### 3.1 SQL 注入测试
```python
# 测试 GET 参数
sql_payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM users--",
    "1' AND 1=1--",
    "1' AND 1=2--",
]

for payload in sql_payloads:
    response = requests.get(f"http://localhost:8000/api/users?search={payload}")
    # 检查是否有 SQL 错误信息泄露
    if "SQL" in response.text or "syntax" in response.text:
        print(f"可能存在 SQL 注入: {payload}")

# 测试 POST 数据
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "admin' OR '1'='1",
    "password": "anything"
})
# 应该返回 400 或 401,不应该登录成功
```

#### 3.2 NoSQL 注入测试
```python
# 测试 MongoDB 注入
nosql_payloads = [
    {"$gt": ""},
    {"$ne": null},
    {"$regex": ".*"},
]

for payload in nosql_payloads:
    response = requests.post("http://localhost:8000/api/auth/login", json={
        "email": payload,
        "password": "anything"
    })
    # 应该被拒绝
```

#### 3.3 命令注入测试
```python
# 测试文件名注入
command_payloads = [
    "test.jpg; ls -la",
    "test.jpg && cat /etc/passwd",
    "test.jpg | whoami",
]

for payload in command_payloads:
    files = {"file": (payload, b"fake image data")}
    response = requests.post("http://localhost:8000/api/check-ins/123/photo",
        files=files)
    # 应该被拒绝或安全处理
```

### 4. XSS 测试

#### 4.1 反射型 XSS
```python
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
]

for payload in xss_payloads:
    # 测试评论功能
    response = requests.post("http://localhost:8000/api/comments", json={
        "plan_id": "123",
        "content": payload
    })
    
    # 获取评论
    response = requests.get("http://localhost:8000/api/comments?plan_id=123")
    
    # 检查是否被转义
    if "<script>" in response.text:
        print(f"XSS 漏洞: {payload}")
```

#### 4.2 存储型 XSS
```python
# 在用户昵称中注入
response = requests.put("http://localhost:8000/api/users/123", json={
    "nickname": "<script>alert('XSS')</script>"
})

# 查看用户信息
response = requests.get("http://localhost:8000/api/users/123")
# 应该被转义
```

### 5. CSRF 测试

```html
<!-- 创建恶意页面 csrf_test.html -->
<!DOCTYPE html>
<html>
<body>
<form action="http://localhost:8000/api/betting-plans" method="POST">
    <input type="hidden" name="bet_amount" value="1000">
    <input type="hidden" name="start_date" value="2024-01-01">
    <input type="hidden" name="end_date" value="2024-01-31">
</form>
<script>
    document.forms[0].submit();
</script>
</body>
</html>
```

```python
# 测试 CSRF 保护
import requests

# 不带 CSRF 令牌的请求
response = requests.post("http://localhost:8000/api/betting-plans", json={
    "bet_amount": 100,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
})

# 应该返回 403
assert response.status_code == 403
```

### 6. 文件上传测试

#### 6.1 恶意文件上传
```python
# 测试上传 PHP 文件
php_shell = b"<?php system($_GET['cmd']); ?>"
files = {"file": ("shell.php", php_shell, "image/jpeg")}
response = requests.post("http://localhost:8000/api/check-ins/123/photo",
    files=files)

# 应该被拒绝

# 测试上传大文件
large_file = b"A" * (10 * 1024 * 1024)  # 10MB
files = {"file": ("large.jpg", large_file, "image/jpeg")}
response = requests.post("http://localhost:8000/api/check-ins/123/photo",
    files=files)

# 应该被限制
```

#### 6.2 路径遍历测试
```python
# 测试路径遍历
path_payloads = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/passwd",
]

for payload in path_payloads:
    response = requests.get(f"http://localhost:8000/api/files/{payload}")
    # 应该返回 400 或 404
```

### 7. 业务逻辑测试

#### 7.1 资金操作测试
```python
# 测试负数金额
response = requests.post("http://localhost:8000/api/betting-plans", json={
    "bet_amount": -100,  # 负数
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
})
# 应该被拒绝

# 测试余额不足
response = requests.post("http://localhost:8000/api/betting-plans", json={
    "bet_amount": 999999999,  # 超大金额
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
})
# 应该返回余额不足错误
```

#### 7.2 竞态条件测试
```python
import threading

def create_plan():
    requests.post("http://localhost:8000/api/betting-plans", json={
        "bet_amount": 100,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })

# 并发创建多个计划
threads = []
for i in range(10):
    t = threading.Thread(target=create_plan)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# 检查资金是否正确冻结
```

#### 7.3 重放攻击测试
```python
# 1. 捕获支付请求
payment_request = {
    "amount": 100,
    "timestamp": "2024-01-01T00:00:00Z",
    "signature": "abc123"
}

# 2. 重放请求
for i in range(5):
    response = requests.post("http://localhost:8000/api/payments/charge",
        json=payment_request)
    
# 应该只成功一次(幂等性)
```

### 8. API 限流测试

```python
import time

# 测试请求限流
success_count = 0
for i in range(150):
    response = requests.get("http://localhost:8000/api/users/123")
    if response.status_code == 200:
        success_count += 1
    elif response.status_code == 429:
        print(f"限流生效: 第 {i+1} 次请求")
        break
    time.sleep(0.1)

# 应该在 100 次左右被限流
assert success_count <= 100
```

### 9. 敏感信息泄露测试

#### 9.1 错误信息泄露
```python
# 触发各种错误
test_cases = [
    ("http://localhost:8000/api/users/invalid_id", "无效 ID"),
    ("http://localhost:8000/api/users/999999", "不存在的用户"),
    ("http://localhost:8000/api/invalid_endpoint", "无效端点"),
]

for url, desc in test_cases:
    response = requests.get(url)
    # 检查是否泄露敏感信息
    sensitive_keywords = ["stack trace", "SQL", "database", "password", "secret"]
    for keyword in sensitive_keywords:
        if keyword.lower() in response.text.lower():
            print(f"敏感信息泄露 ({desc}): {keyword}")
```

#### 9.2 版本信息泄露
```python
# 检查响应头
response = requests.get("http://localhost:8000")
headers = response.headers

# 不应该暴露服务器版本
if "Server" in headers:
    print(f"服务器版本泄露: {headers['Server']}")

if "X-Powered-By" in headers:
    print(f"技术栈泄露: {headers['X-Powered-By']}")
```

### 10. 移动端测试

#### 10.1 Android 安全测试
```bash
# 反编译 APK
apktool d app.apk

# 查找硬编码的密钥
grep -r "api_key" app/
grep -r "secret" app/
grep -r "password" app/

# 检查网络安全配置
cat app/res/xml/network_security_config.xml

# 使用 MobSF 扫描
python3 manage.py runserver
# 上传 APK 到 http://localhost:8000
```

#### 10.2 iOS 安全测试
```bash
# 使用 class-dump 导出头文件
class-dump -H app.ipa -o headers/

# 查找敏感字符串
strings app.ipa | grep -i "api"
strings app.ipa | grep -i "key"

# 检查 Info.plist
plutil -p Info.plist
```

## 渗透测试工具

### 自动化工具
- **OWASP ZAP**: Web 应用安全扫描
- **Burp Suite**: 拦截和修改 HTTP 请求
- **Nmap**: 端口扫描
- **SQLMap**: SQL 注入测试
- **Nikto**: Web 服务器扫描
- **MobSF**: 移动应用安全扫描

### 手动测试工具
- **Postman**: API 测试
- **curl**: 命令行 HTTP 客户端
- **Python requests**: 编程测试

## 渗透测试报告模板

### 渗透测试报告

**测试日期**: YYYY-MM-DD  
**测试人员**: [姓名]  
**测试范围**: 
- 后端 API
- Android 客户端
- iOS 客户端

**执行摘要**:
[简要描述测试结果和主要发现]

**发现的漏洞**:

#### 1. [高危] SQL 注入漏洞
- **位置**: /api/users?search=
- **描述**: 搜索参数未正确过滤,可能导致 SQL 注入
- **影响**: 攻击者可以读取、修改或删除数据库数据
- **复现步骤**:
  1. 访问 /api/users?search=' OR '1'='1
  2. 观察返回所有用户数据
- **修复建议**: 使用参数化查询或 ORM
- **CVSS 评分**: 9.0 (Critical)

#### 2. [中危] XSS 漏洞
- **位置**: /api/comments
- **描述**: 评论内容未转义,存在存储型 XSS
- **影响**: 攻击者可以窃取用户会话或执行恶意操作
- **复现步骤**:
  1. 发表评论: `<script>alert('XSS')</script>`
  2. 其他用户查看评论时触发
- **修复建议**: 对输出内容进行 HTML 转义
- **CVSS 评分**: 6.5 (Medium)

**安全评分**: XX/100

**总体评估**:
[安全状况总结]

**优先修复建议**:
1. [高危漏洞修复]
2. [中危漏洞修复]

**下次测试时间**: YYYY-MM-DD
