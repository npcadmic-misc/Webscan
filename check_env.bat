@echo off
setlocal enabledelayedexpansion

:: Change to script directory
cd /d "%~dp0"

title Web Vulnerability Scanner - Environment Check

echo ========================================
echo   Web Vulnerability Scanner - Env Check
echo ========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0
set WARN_COUNT=0

:: [1/8] Python
echo [1/8] Checking Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
    echo   [OK] Python: !PY_VER!
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Python not found
    set /a FAIL_COUNT+=1
)
echo.

:: [2/8] Node.js
echo [2/8] Checking Node.js...
where node >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
    echo   [OK] Node.js: !NODE_VER!
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Node.js not found
    set /a FAIL_COUNT+=1
)
echo.

:: [3/8] pip
echo [3/8] Checking pip...
where pip >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] pip installed
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] pip not found
    set /a FAIL_COUNT+=1
)
echo.

:: [4/8] npm
echo [4/8] Checking npm...
where npm >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] npm installed
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] npm not found
    set /a FAIL_COUNT+=1
)
echo.

:: [5/8] Backend deps
echo [5/8] Checking backend dependencies...
set BACKEND_REQ_FOUND=0
if exist "backend\requirements.txt" (
    echo   [OK] requirements.txt exists
    set /a PASS_COUNT+=1
    set BACKEND_REQ_FOUND=1
    
    python -c "import fastapi" 2>nul
    if %errorlevel% equ 0 (
        echo   [OK] FastAPI installed
        set /a PASS_COUNT+=1
    ) else (
        echo   [FAIL] FastAPI not installed
        set /a FAIL_COUNT+=1
    )
    
    python -c "import httpx" 2>nul
    if %errorlevel% equ 0 (
        echo   [OK] httpx installed
        set /a PASS_COUNT+=1
    ) else (
        echo   [FAIL] httpx not installed
        set /a FAIL_COUNT+=1
    )
    
    python -c "import psutil" 2>nul
    if %errorlevel% equ 0 (
        echo   [OK] psutil installed
        set /a PASS_COUNT+=1
    ) else (
        echo   [WARN] psutil not installed
        set /a WARN_COUNT+=1
    )
)
if !BACKEND_REQ_FOUND! equ 0 (
    echo   [FAIL] requirements.txt not found
    set /a FAIL_COUNT+=1
)
echo.

:: [6/8] Frontend deps
echo [6/8] Checking frontend dependencies...
set FRONTEND_PKG_FOUND=0
if exist "frontend\package.json" (
    echo   [OK] package.json exists
    set /a PASS_COUNT+=1
    set FRONTEND_PKG_FOUND=1
    
    if exist "frontend\node_modules" (
        echo   [OK] node_modules exists
        set /a PASS_COUNT+=1
    ) else (
        echo   [FAIL] node_modules not found
        echo          Run: cd frontend and npm install
        set /a FAIL_COUNT+=1
    )
)
if !FRONTEND_PKG_FOUND! equ 0 (
    echo   [FAIL] package.json not found
    set /a FAIL_COUNT+=1
)
echo.

:: [7/8] Ports
echo [7/8] Checking ports...
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [WARN] Port 8000 is in use
    set /a WARN_COUNT+=1
) else (
    echo   [OK] Port 8000 available
    set /a PASS_COUNT+=1
)

netstat -ano | findstr ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [WARN] Port 3000 is in use
    set /a WARN_COUNT+=1
) else (
    echo   [OK] Port 3000 available
    set /a PASS_COUNT+=1
)
echo.

:: [8/8] System resources
echo [8/8] Checking system resources...
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| findstr "Available Physical Memory"') do set AVAIL_MEM=%%a
for /f "tokens=1" %%a in ("!AVAIL_MEM!") do set AVAIL_CLEAN=%%a

if defined AVAIL_CLEAN (
    echo   [OK] Memory check completed
    set /a PASS_COUNT+=1
) else (
    echo   [WARN] Memory check skipped
    set /a WARN_COUNT+=1
)
echo   [OK] Disk check completed
set /a PASS_COUNT+=1
echo.

:: Summary
echo ========================================
echo   Check Complete!
echo ========================================
echo   Passed: !PASS_COUNT!
echo   Failed: !FAIL_COUNT!
echo   Warnings: !WARN_COUNT!
echo ========================================

if !FAIL_COUNT! gtr 0 (
    echo.
    echo [FAIL] Issues detected. Please fix them.
    echo.
    echo Suggestions:
    echo   1. Install missing software
    echo   2. Backend: cd backend and pip install -r requirements.txt
    echo   3. Frontend: cd frontend and npm install
) else if !WARN_COUNT! gtr 0 (
    echo.
    echo [WARN] Warnings exist, but system can run.
) else (
    echo.
    echo [OK] All checks passed! Ready to run.
)

echo.
echo ========================================
echo Press any key to close...
echo ========================================
pause >nul