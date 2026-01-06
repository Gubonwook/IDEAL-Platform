@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ==================================================
echo      Starting Automated ALIGNN Processing
echo ==================================================
echo.

set /p RESETCACHE="Do you want to delete the coefficient cache? (y/n): "
if /i "%RESETCACHE%"=="y" (
    if exist coef_cache.json (
        del coef_cache.json
        echo Cache has been deleted.
    ) else (
        echo No cache file found to delete.
    )
) else (
    echo Maintaining existing cache.
)
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
echo [2/2] Running 'alignn_play.py' script...
echo.
python alignn_play.py

if "!ERRORLEVEL!" neq "0" (
    echo.
    echo ^>^>^> ERROR: Task interrupted with errors.
) else (
    echo.
    echo ==================================================
    echo      All batch tasks completed successfully.
    echo ==================================================
)

# if exist postprocess_top10.py (
#     python postprocess_top10.py
# )

echo.
pause
