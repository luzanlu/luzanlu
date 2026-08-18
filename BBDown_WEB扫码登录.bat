@echo off
chcp 936 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python，无法运行 WEB 登录修复。
    pause
    exit /b 1
)
python "%~dp0BBDown_WEB_login.py" %*
set "RC=%ERRORLEVEL%"
echo.
if /i not "%~1"=="--self-test" pause
exit /b %RC%
