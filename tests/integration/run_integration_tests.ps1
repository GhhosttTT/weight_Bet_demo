# 跨平台集成测试执行脚本 (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "减肥对赌 APP - 跨平台集成测试" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 环境
Write-Host "检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 环境正常: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误: 未找到 Python" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Yellow
pip install -q pytest requests pytest-html
Write-Host "✓ 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 检查后端服务
Write-Host "检查后端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ 后端服务正常" -ForegroundColor Green
} catch {
    Write-Host "⚠ 警告: 后端服务未运行" -ForegroundColor Yellow
    Write-Host "请先启动后端服务:" -ForegroundColor Yellow
    Write-Host "  cd backend; python manage.py runserver" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "是否继续测试? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}
Write-Host ""

# 创建测试报告目录
$reportDir = "test_reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "$reportDir/integration_test_report_$timestamp.html"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "开始执行集成测试" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 运行测试
Write-Host "1. 运行跨平台基础功能测试..." -ForegroundColor Yellow
pytest test_cross_platform.py `
    -v `
    --html=$reportFile `
    --self-contained-html `
    --tb=short `
    --color=yes

$testExitCode1 = $LASTEXITCODE

Write-Host ""
Write-Host "2. 运行结算流程测试..." -ForegroundColor Yellow
pytest test_settlement.py -v -s --tb=short --color=yes

$testExitCode2 = $LASTEXITCODE

Write-Host ""
Write-Host "3. 运行支付流程测试..." -ForegroundColor Yellow
pytest test_payment.py -v -s --tb=short --color=yes

$testExitCode3 = $LASTEXITCODE

# 计算总体测试结果
$testExitCode = $testExitCode1 + $testExitCode2 + $testExitCode3

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($testExitCode -eq 0) {
    Write-Host "✓ 所有测试通过" -ForegroundColor Green
    Write-Host ""
    Write-Host "测试报告已生成: $reportFile" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "✗ 部分测试失败" -ForegroundColor Red
    Write-Host ""
    Write-Host "测试报告已生成: $reportFile" -ForegroundColor Cyan
    Write-Host "请查看报告了解详细信息" -ForegroundColor Yellow
    exit 1
}
