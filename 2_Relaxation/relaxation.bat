@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

cd /d "%~dp0"

echo.
echo ==================================================================
echo      Starting Structure Relaxation (CHGNet) Script
echo ==================================================================
echo.

echo [1/2] Activating Conda environment 'ideal_platform'...
call conda activate ideal_platform

if "!ERRORLEVEL!" neq "0" (
    echo.
    echo ^>^>^> ERROR: Could not activate 'ideal_platform' environment.
    pause
    exit /b
)

echo.
echo [2/2] Running 'total.py' script...
echo.
python total.py

if "!ERRORLEVEL!" neq "0" (
    echo.
    echo ^>^>^> ERROR: An error occurred during Python script execution.
) else (
    echo.
    echo ==================================================================
    echo      🎉 All tasks completed successfully! 🎉
    echo ==================================================================
)

echo.
pause
