# Web Vulnerability Scanner - Startup Manager
# PowerShell Script

Clear-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Web Vulnerability Scanner - Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "backend"
$frontendDir = Join-Path $scriptDir "frontend"

function Show-Menu {
    Write-Host "Select an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] Start Backend Only (FastAPI)" -ForegroundColor Green
    Write-Host "  [2] Start Frontend Only (Vue Dev Server)" -ForegroundColor Green
    Write-Host "  [3] Start Both Backend and Frontend (Recommended)" -ForegroundColor Green
    Write-Host "  [4] CLI Mode Scan" -ForegroundColor Green
    Write-Host "  [5] Check Service Status" -ForegroundColor Green
    Write-Host "  [0] Exit" -ForegroundColor Red
    Write-Host ""
}

function Start-Backend {
    Write-Host ""
    Write-Host "Starting backend service..." -ForegroundColor Cyan
    Write-Host "Backend URL: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $backendDir) {
        Set-Location $backendDir
        
        Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
        python -c "import fastapi" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing dependencies..." -ForegroundColor Yellow
            pip install -r requirements.txt
        }
        
        Write-Host ""
        Write-Host "Starting FastAPI server..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    } else {
        Write-Host "Error: backend directory not found" -ForegroundColor Red
    }
}

function Start-Frontend {
    Write-Host ""
    Write-Host "Starting frontend service..." -ForegroundColor Cyan
    Write-Host "Frontend URL: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $frontendDir) {
        Set-Location $frontendDir
        
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing dependencies..." -ForegroundColor Yellow
            npm install
        }
        
        Write-Host ""
        Write-Host "Starting Vue dev server..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        
        npm run dev
    } else {
        Write-Host "Error: frontend directory not found" -ForegroundColor Red
    }
}

function Start-Both {
    Write-Host ""
    Write-Host "Starting both backend and frontend..." -ForegroundColor Cyan
    Write-Host "Backend URL: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Frontend URL: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Starting backend service..." -ForegroundColor Green
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -WindowStyle Normal
    
    Start-Sleep -Seconds 3
    
    Write-Host "Starting frontend service..." -ForegroundColor Green
    Set-Location $frontendDir
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Services Started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Tip: Close this window to stop all services" -ForegroundColor Yellow
    Write-Host ""
    
    npm run dev
}

function Start-CLI {
    Write-Host ""
    Write-Host "Starting CLI mode..." -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $backendDir) {
        Set-Location $backendDir
        
        python -c "import fastapi" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing dependencies..." -ForegroundColor Yellow
            pip install -r requirements.txt
        }
        
        Write-Host ""
        Write-Host "Starting CLI scanner..." -ForegroundColor Green
        Write-Host ""
        
        python cli.py
    } else {
        Write-Host "Error: backend directory not found" -ForegroundColor Red
    }
}

function Check-Status {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Service Status Check" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[Backend Service]" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  Status: Running" -ForegroundColor Green
            Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  Status: Not Running" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "[Frontend Service]" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  Status: Running" -ForegroundColor Green
            Write-Host "  URL: http://localhost:3000" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  Status: Not Running" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "[Port Usage]" -ForegroundColor Yellow
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($port8000) {
        Write-Host "  Port 8000: In use (PID: $($port8000.OwningProcess))" -ForegroundColor Green
    } else {
        Write-Host "  Port 8000: Available" -ForegroundColor Cyan
    }
    
    $port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($port3000) {
        Write-Host "  Port 3000: In use (PID: $($port3000.OwningProcess))" -ForegroundColor Green
    } else {
        Write-Host "  Port 3000: Available" -ForegroundColor Cyan
    }
    Write-Host ""
}

while ($true) {
    Show-Menu
    
    $choice = Read-Host "Enter option (0-5)"
    
    switch ($choice) {
        "1" {
            Start-Backend
        }
        "2" {
            Start-Frontend
        }
        "3" {
            Start-Both
        }
        "4" {
            Start-CLI
        }
        "5" {
            Check-Status
            Write-Host ""
            Write-Host "Press any key to return to menu..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Clear-Host
        }
        "0" {
            Write-Host ""
            Write-Host "Goodbye!" -ForegroundColor Green
            break
        }
        default {
            Write-Host ""
            Write-Host "Invalid option, please try again" -ForegroundColor Red
            Start-Sleep -Seconds 1
            Clear-Host
        }
    }
}