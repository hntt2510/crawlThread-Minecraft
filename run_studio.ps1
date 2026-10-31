<#
.SYNOPSIS
    Khởi động Threads Comment Video Studio trên Windows 10/11
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   THREADS COMMENT VIDEO STUDIO - LOCAL-FIRST STUDIO     " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Check Python Venv
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[1/3] Đang tạo môi trường ảo Python 3.12..." -ForegroundColor Yellow
    uv venv .venv --python 3.12
    uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
} else {
    Write-Host "[1/3] Môi trường Python đã sẵn sàng." -ForegroundColor Green
}

# 2. Check Frontend Build
if (-not (Test-Path ".\frontend\dist\index.html")) {
    Write-Host "[2/3] Đang biên dịch giao diện React Studio..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    npm run build
    Set-Location $ScriptDir
} else {
    Write-Host "[2/3] Giao diện Studio đã sẵn sàng." -ForegroundColor Green
}

# 3. Start Server & Open Browser
Write-Host "[3/3] Đang khởi động máy chủ tại http://127.0.0.1:8000..." -ForegroundColor Cyan
Write-Host "Bấm Ctrl+C trong cửa sổ này nếu bạn muốn dừng máy chủ." -ForegroundColor Gray

# Open browser after 2 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

$env:PYTHONPATH = "."
& .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
