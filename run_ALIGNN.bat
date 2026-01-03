@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ==================================================
echo      ALIGNN 전체 자동 처리를 시작합니다.
echo ==================================================
echo.

:: === [추가] 보정계수 캐시 초기화 선택 ===
set /p RESETCACHE="보정계수 캐시를 삭제하시겠습니까? (y/n): "
if /i "%RESETCACHE%"=="y" (
    if exist coef_cache.json (
        del coef_cache.json
        echo 캐시가 삭제되었습니다.
    ) else (
        echo 삭제할 캐시 파일이 없습니다.
    )
) else (
    echo 기존 캐시를 유지합니다.
)
echo.

REM [수정] GPU용으로 만든 Conda 환경을 활성화합니다.
call conda activate my_alignn

REM 스크립트 실행
python alignn_play.py

REM 파이썬 스크립트의 성공/실패 여부를 확인
if "!ERRORLEVEL!" neq "0" (
    echo.
    echo ^>^>^> ERROR: 작업이 오류와 함께 중단되었습니다.
) else (
    echo.
    echo ==================================================
    echo      모든 배치 작업이 성공적으로 완료되었습니다.
    echo ==================================================
)

python postprocess_top10.py

REM [수정] 작업 완료 후 창이 바로 닫히지 않도록 주석을 해제합니다.
pause
