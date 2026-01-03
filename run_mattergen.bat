@echo off
rem 한글 출력을 위한 코드 페이지 설정
chcp 65001 > nul

rem 배치 파일이 있는 폴더로 작업 위치를 강제 이동
cd /d "%~dp0"

echo.
echo --- [ Anaconda 환경 활성화 중... ] ---
echo     환경 이름: mattergen_new
echo.

rem [수정] 배치 파일에서 Conda 환경을 직접 활성화합니다.
call "C:\Users\HBRLRG\anaconda3\condabin\conda.bat" activate mattergen_new

rem 환경 활성화 성공 여부 확인
if %ERRORLEVEL% neq 0 (
    echo.
    echo ^>^>^> ERROR: 'mattergen_new' 환경을 활성화할 수 없습니다.
    echo.
    pause
    exit /b 1
)

echo.
echo --- [ CSV 설정 기반 MatterGen 자동 처리 시작 ] ---
echo.

rem 파이썬 스크립트를 실행합니다.
python run_mattergen_from_excel.py

echo.
echo --- [ 스크립트 실행 완료 ] ---
echo.
pause