# 项目脚本目录

本目录包含项目的自动化脚本，用于快速搭建和运行项目。

## 脚本列表

### Windows PowerShell 脚本

| 脚本 | 功能 | 用法 |
|------|------|------|
| `setup.ps1` | 项目快速初始化向导 | `.\scripts\setup.ps1` |
| `start-backend.ps1` | 启动后端服务 | `.\scripts\start-backend.ps1` |
| `run-tests.ps1` | 运行所有测试 | `.\scripts\run-tests.ps1` |

## 使用说明

### 1. 快速初始化项目

在 Windows PowerShell 中运行：

```powershell
.\scripts\setup.ps1
```

这个脚本会：
- 检查 Python 环境
- 设置后端虚拟环境和依赖
- 提示如何打开 Android 和 iOS 项目

### 2. 启动后端

```powershell
.\scripts\start-backend.ps1
```

后端将在 http://localhost:8000 启动

- API 文档：http://localhost:8000/api/docs
- ReDoc 文档：http://localhost:8000/api/redoc

### 3. 运行测试

```powershell
.\scripts\run-tests.ps1
```

这将运行：
- 后端所有单元测试
- Android 所有单元测试

## 注意事项

- 所有脚本需要在项目根目录运行
- 确保已安装 Python 3.8+
- iOS 开发需要 macOS 和 Xcode
