@echo off
rem Set code page to UTF-8 for proper character display
chcp 65001 > nul

rem Force working directory to the batch file location
cd /d "%~dp0"

echo.
echo --- [ Activating Conda Environment... ] ---
echo     Environment Name: ideal_platform
echo.

rem Activate Conda environment
call conda activate ideal_platform

rem Check if activation was successful
if %ERRORLEVEL% neq 0 (
    echo.
    echo ^>^>^> ERROR: Could not activate 'ideal_platform' environment.
    echo Please check if 'conda' is in your PATH or update the activation command.
    echo.
    pause
    exit /b 1
)

echo.
echo --- [ Starting Automated MatterGen Processing from CSV ] ---
echo.

rem Run the Python script
python run_mattergen_from_excel.py

echo.
echo --- [ Script Execution Completed ] ---
echo.
pause
