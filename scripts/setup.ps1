# 项目快速启动脚本 - Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  减肥对赌 APP - 快速启动向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[1/5] 检查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 未安装，请先安装 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查 Node.js (可选)
Write-Host ""
Write-Host "[2/5] 检查开发环境..." -ForegroundColor Yellow

# 检查后端依赖
Write-Host ""
Write-Host "[3/5] 设置后端..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "..\backend"
if (Test-Path $backendPath) {
    Set-Location $backendPath
    Write-Host "  进入后端目录: $backendPath" -ForegroundColor Gray
    
    if (-not (Test-Path "venv")) {
        Write-Host "  创建 Python 虚拟环境..." -ForegroundColor Gray
        python -m venv venv
    }
    
    Write-Host "  激活虚拟环境..." -ForegroundColor Gray
    .\venv\Scripts\Activate.ps1
    
    Write-Host "  安装依赖..." -ForegroundColor Gray
    pip install -r requirements.txt
    
    Write-Host "✓ 后端设置完成" -ForegroundColor Green
} else {
    Write-Host "✗ 后端目录不存在" -ForegroundColor Red
}

# 返回项目根目录
Set-Location $PSScriptRoot\..

Write-Host ""
Write-Host "[4/5] 设置 Android..." -ForegroundColor Yellow
$androidPath = Join-Path $PSScriptRoot "..\android"
if (Test-Path $androidPath) {
    Write-Host "  Android 项目位置: $androidPath" -ForegroundColor Gray
    Write-Host "  提示: 使用 Android Studio 打开 android/ 目录" -ForegroundColor Cyan
    Write-Host "✓ Android 项目就绪" -ForegroundColor Green
} else {
    Write-Host "✗ Android 目录不存在" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/5] 设置 iOS..." -ForegroundColor Yellow
$iosPath = Join-Path $PSScriptRoot "..\ios"
if (Test-Path $iosPath) {
    Write-Host "  iOS 项目位置: $iosPath" -ForegroundColor Gray
    Write-Host "  提示: 在 macOS 上使用 Xcode 打开 ios/ 目录" -ForegroundColor Cyan
    Write-Host "  然后运行: pod install" -ForegroundColor Cyan
    Write-Host "✓ iOS 项目就绪" -ForegroundColor Green
} else {
    Write-Host "✗ iOS 目录不存在" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  设置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 启动后端:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 打开 Android 项目:" -ForegroundColor White
Write-Host "     使用 Android Studio 打开 android/ 目录" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 打开 iOS 项目 (macOS):" -ForegroundColor White
Write-Host "     cd ios ; pod install" -ForegroundColor Gray
Write-Host "     使用 Xcode 打开 ios/ 目录" -ForegroundColor Gray
Write-Host ""
