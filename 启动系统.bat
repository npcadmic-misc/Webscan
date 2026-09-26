@echo off
chcp 65001 >nul
title Web Vulnerability Scanner - Launcher

cd /d "%~dp0"

where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell not found
    pause
    exit /b 1
)

powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

pause