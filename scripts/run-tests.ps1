# 运行测试脚本 - Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  运行项目测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Join-Path $PSScriptRoot "..\backend"
$androidPath = Join-Path $PSScriptRoot "..\android"

# 后端测试
Write-Host "[1/2] 运行后端测试..." -ForegroundColor Yellow
if (Test-Path $backendPath) {
    Set-Location $backendPath
    
    if (Test-Path "venv") {
        .\venv\Scripts\Activate.ps1
    }
    
    Write-Host ""
    Write-Host "运行后端单元测试..." -ForegroundColor Gray
    python -m pytest tests/ -v --tb=short
    $backendTestExitCode = $LASTEXITCODE
    
    if ($backendTestExitCode -eq 0) {
        Write-Host "✓ 后端测试通过" -ForegroundColor Green
    } else {
        Write-Host "✗ 后端测试失败" -ForegroundColor Red
    }
} else {
    Write-Host "✗ 后端目录不存在" -ForegroundColor Red
}

# 返回项目根目录
Set-Location $PSScriptRoot\..

# Android 测试
Write-Host ""
Write-Host "[2/2] 运行 Android 测试..." -ForegroundColor Yellow
if (Test-Path $androidPath) {
    Set-Location $androidPath
    
    Write-Host ""
    Write-Host "运行 Android 单元测试..." -ForegroundColor Gray
    .\gradlew.bat testDebugUnitTest
    $androidTestExitCode = $LASTEXITCODE
    
    if ($androidTestExitCode -eq 0) {
        Write-Host "✓ Android 测试通过" -ForegroundColor Green
    } else {
        Write-Host "✗ Android 测试失败" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Android 目录不存在" -ForegroundColor Red
}

# 返回项目根目录
Set-Location $PSScriptRoot\..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试运行完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
