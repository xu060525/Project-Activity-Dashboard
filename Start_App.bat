@echo off
TITLE Project Health Dashboard Launcher
COLOR 0A

echo ==============================================
echo      PROJECT ACTIVITY DASHBOARD
echo      (Local-First Analysis Tool)
echo ==============================================
echo.

:: 1. 检查是否有虚拟环境
if exist venv\Scripts\python.exe (
    echo [System] Using local virtual environment...
    venv\Scripts\python.exe main_launcher.py
) else (
    echo [System] Virtual environment not found. Using system Python...
    python main_launcher.py
)

pause