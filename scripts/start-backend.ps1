# 后端快速启动脚本 - Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Join-Path $PSScriptRoot "..\backend"

if (-not (Test-Path $backendPath)) {
    Write-Host "✗ 后端目录不存在: $backendPath" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 安装依赖（如果需要）
Write-Host "检查依赖..." -ForegroundColor Yellow
pip install -r requirements.txt -q

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  后端服务启动中..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API 文档: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "ReDoc 文档: http://localhost:8000/api/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
