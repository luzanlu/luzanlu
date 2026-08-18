# -*- coding: utf-8 -*-
from pathlib import Path

text = r'''@echo off
chcp 936 >nul
setlocal EnableExtensions EnableDelayedExpansion
TITLE BBDown 统一下载器 - 生成分发脚本
color 0A

echo ========================================
echo  BBDown 统一下载器
echo  选模式 - 输链接 - 选集数 - 选画质 - 生成bat
echo  支持连续解析多个链接, Ctrl+C 退出
echo ========================================
echo.

:SelectMode
echo [解析模式]
echo   1. TV   (加 -tv, 适合番剧/纪录片)
echo   2. WEB  (默认网页接口)
echo   3. 扫码登录 TV 端
echo   4. 扫码登录 WEB 端
set "MODE_INPUT="
set /p MODE_INPUT=请输入模式 1/2/3/4 [默认2]:
if "!MODE_INPUT!"=="" set "MODE_INPUT=2"
if "!MODE_INPUT!"=="3" goto LoginTV
if "!MODE_INPUT!"=="4" goto LoginWEB
if not "!MODE_INPUT!"=="1" if not "!MODE_INPUT!"=="2" (
    echo [错误] 无效模式: !MODE_INPUT!
    echo.
    goto SelectMode
)
set "MODE_FLAG="
set "MODE_AUTH="
set "TV_ACCESS_TOKEN="
set "MODE_NAME=WEB"
if "!MODE_INPUT!"=="1" (
    set "MODE_FLAG=-tv"
    if not exist "%~dp0BBDownTV.data" (
        echo [错误] 缺少 BBDownTV.data，无法使用 TV 模式
        goto End
    )
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0BBDownTV.data") do if /I "%%A"=="access_token" set "TV_ACCESS_TOKEN=%%B"
    if not defined TV_ACCESS_TOKEN (
        echo [错误] BBDownTV.data 中没有有效 access_token
        goto End
    )
    set "MODE_AUTH=--access-token=!TV_ACCESS_TOKEN!"
    set "MODE_NAME=TV"
)
echo 已选择: !MODE_NAME!
echo.

:AskURL
for /f "delims==" %%v in ('set val_dfn_ 2^>nul') do set "%%v="
for /f "delims==" %%v in ('set val_enc_ 2^>nul') do set "%%v="
for /f "delims==" %%v in ('set val_rate_ 2^>nul') do set "%%v="
for /f "delims==" %%v in ('set val_size_ 2^>nul') do set "%%v="
set "URL="
ver >nul
set /p URL=请输入视频地址 或 AV/BV/EP/SS (Ctrl+C 退出):
if errorlevel 1 goto :End
if "!URL!"=="" (
    echo [错误] 链接不能为空
    goto AskURL
)
echo.

if "!MODE_FLAG!"=="-tv" (
    BBDown -tv !MODE_AUTH! -info "!URL!" -p 1 > _temp_quality.txt 2>&1 <nul
) else (
    BBDown -info "!URL!" -p 1 > _temp_quality.txt 2>&1 <nul
)

echo 全部集数:
echo ----------------------------------------
findstr /R /C:" - P[0-9][0-9]*:" _temp_quality.txt
echo ----------------------------------------
echo 选择方式: 单选1  多选1,3,5  范围1-5  全部ALL  最新LAST
set /p EPISODES=请输入集数 [默认ALL]:
if "!EPISODES!"=="" set "EPISODES=ALL"
echo 集数: !EPISODES!
echo.

set "QUALITY_EP=!EPISODES!"
for /f "tokens=1 delims=,-" %%A in ("!QUALITY_EP!") do set "QUALITY_EP=%%A"
if /I "!EPISODES!"=="ALL" set "QUALITY_EP=1"
if /I "!EPISODES!"=="LAST" (
    set "LAST_P_LINE="
    for /f "tokens=2 delims=]" %%A in ('findstr /R /C:" - P[0-9][0-9]*:" _temp_quality.txt') do set "LAST_P_LINE=%%A"
    for /f "tokens=2 delims=P:" %%A in ("!LAST_P_LINE!") do set "QUALITY_EP=%%A"
)
echo 正在读取 P!QUALITY_EP! 画质...
if "!MODE_FLAG!"=="-tv" (
    BBDown -tv !MODE_AUTH! -info "!URL!" -p !QUALITY_EP! > _temp_quality.txt 2>&1 <nul
) else (
    BBDown -info "!URL!" -p !QUALITY_EP! > _temp_quality.txt 2>&1 <nul
)
echo.

set "v_count=0"
for /f "tokens=2,4,6,8 delims=[]" %%A in ('type _temp_quality.txt ^| findstr /C:"] ["') do (
    if not "%%D"=="" (
        set "val_dfn_!v_count!=%%A"
        set "val_enc_!v_count!=%%B"
        set "val_rate_!v_count!=%%C"
        set "val_size_!v_count!=%%D"
        set /a v_count+=1
    )
)

if !v_count! EQU 0 (
    echo [错误] 没有抓到视频流, 检查链接/模式/网络
    echo 原始输出:
    type _temp_quality.txt
    del _temp_quality.txt 2>nul
    echo.
    goto AskURL
)

set /a max_idx=v_count-1
echo 可用画质:
echo ----------------------------------------
for /L %%i in (0,1,!max_idx!) do (
    if defined val_dfn_%%i (
        echo   [%%i] [!val_dfn_%%i!] [!val_enc_%%i!] [!val_rate_%%i!] [!val_size_%%i!]
    )
)
echo ----------------------------------------
echo 选择方式: 单选0  多选0,2,4  范围0-2
echo.

:PickQuality
set "SEL_IDX="
set /p SEL_IDX=[2/3] 请输入画质序号:
if "!SEL_IDX!"=="" (
    echo [错误] 序号不能为空
    goto PickQuality
)

set "TARGET_DFN="
set "TARGET_ENC="
set "SEL_OK=0"
for /f "tokens=1,2 delims=-" %%A in ("!SEL_IDX!") do (
    if not "%%B"=="" (
        for /L %%i in (%%A,1,%%B) do (
            if defined val_dfn_%%i (
                if defined TARGET_DFN (
                    set "TARGET_DFN=!TARGET_DFN!,!val_dfn_%%i!"
                    set "TARGET_ENC=!TARGET_ENC!,!val_enc_%%i!"
                ) else (
                    set "TARGET_DFN=!val_dfn_%%i!"
                    set "TARGET_ENC=!val_enc_%%i!"
                )
                set "SEL_OK=1"
            )
        )
    )
)
if "!SEL_OK!"=="0" (
    for %%i in (!SEL_IDX!) do (
        if defined val_dfn_%%i (
            if defined TARGET_DFN (
                set "TARGET_DFN=!TARGET_DFN!,!val_dfn_%%i!"
                set "TARGET_ENC=!TARGET_ENC!,!val_enc_%%i!"
            ) else (
                set "TARGET_DFN=!val_dfn_%%i!"
                set "TARGET_ENC=!val_enc_%%i!"
            )
            set "SEL_OK=1"
        )
    )
)
if "!SEL_OK!"=="0" (
    echo [错误] 无效序号
    goto PickQuality
)

set "VIDEO_TITLE="
set "TITLE_LINE="
for /f "tokens=2 delims=]" %%A in ('findstr /C:" - 视频标题:" _temp_quality.txt') do if not defined TITLE_LINE set "TITLE_LINE=%%A"
set "VIDEO_TITLE=!TITLE_LINE:* - 视频标题: =!"
if not defined VIDEO_TITLE set "VIDEO_TITLE=BBDown"

set "BAT_LABEL=[!EPISODES!]"
set "PAGE_TITLE="
for /f "tokens=5 delims=[]" %%A in ('findstr /C:" - P!EPISODES!:" _temp_quality.txt') do if not defined PAGE_TITLE set "PAGE_TITLE=%%A"
if defined PAGE_TITLE (
    set "PAD_EP=!EPISODES!"
    if !EPISODES! LSS 10 set "PAD_EP=0!EPISODES!"
    set "BAT_LABEL=[P!PAD_EP!]!PAGE_TITLE!"
)

set "SAFE_TITLE=!VIDEO_TITLE:\=_!"
set "SAFE_TITLE=!SAFE_TITLE:/=_!"
set "SAFE_TITLE=!SAFE_TITLE::=_!"
set "SAFE_TITLE=!SAFE_TITLE:?=_!"
set "SAFE_LABEL=!BAT_LABEL:\=_!"
set "SAFE_LABEL=!SAFE_LABEL:/=_!"
set "SAFE_LABEL=!SAFE_LABEL::=_!"
set "SAFE_LABEL=!SAFE_LABEL:?=_!"
set "OUT_FILE=%~dp0!SAFE_TITLE! !SAFE_LABEL! [!TARGET_ENC!].bat"

(
    echo @echo off
    echo chcp 936 ^>nul
    echo pushd "%%~dp0"
    echo TITLE BBDown !MODE_NAME! 下载
    echo color 0A
    echo echo 模式=!MODE_NAME!  集数=!EPISODES!
    echo echo 画质=!TARGET_DFN!  编码=!TARGET_ENC!
    echo echo 链接=!URL!
    echo echo.
    echo if exist aria2c.exe ^(
    echo     echo 检测到 aria2c.exe, 使用 Aria2
    echo     set "EXTRA_CMD=--use-aria2c"
    echo ^) else ^(
    echo     echo 未检测到 aria2c.exe, 使用 BBDown 默认下载
    echo     set "EXTRA_CMD="
    echo ^)
    if "!MODE_FLAG!"=="-tv" (
        echo if not exist "%%~dp0BBDownTV.data" ^(
        echo     echo [错误] 缺少 BBDownTV.data
        echo     pause
        echo     exit /b 1
        echo ^)
        echo set "TV_ACCESS_TOKEN="
        echo for /f "usebackq tokens=1,* delims==" %%%%A in ^("%%~dp0BBDownTV.data"^) do if /I "%%%%A"=="access_token" set "TV_ACCESS_TOKEN=%%%%B"
        echo if not defined TV_ACCESS_TOKEN ^(
        echo     echo [错误] BBDownTV.data 中没有有效 access_token
        echo     pause
        echo     exit /b 1
        echo ^)
    )
    echo echo 开始下载...
    if "!MODE_FLAG!"=="-tv" (
        echo BBDown !MODE_FLAG! --access-token=%%TV_ACCESS_TOKEN%% --skip-cover "!URL!" -p !EPISODES! --dfn-priority "!TARGET_DFN!" --encoding-priority "!TARGET_ENC!" --file-pattern "^<videoTitle^> [P^<pageNumberWithZero^>]^<pageTitle^> [^<videoCodecs^>]" --multi-file-pattern "^<videoTitle^> [P^<pageNumberWithZero^>]^<pageTitle^> [^<videoCodecs^>]" %%EXTRA_CMD%% --work-dir ".\哔哩动画"
    ) else (
        echo BBDown !MODE_FLAG! !MODE_AUTH! --skip-cover "!URL!" -p !EPISODES! --dfn-priority "!TARGET_DFN!" --encoding-priority "!TARGET_ENC!" --file-pattern "^<videoTitle^> [P^<pageNumberWithZero^>]^<pageTitle^> [^<videoCodecs^>]" --multi-file-pattern "^<videoTitle^> [P^<pageNumberWithZero^>]^<pageTitle^> [^<videoCodecs^>]" %%EXTRA_CMD%% --work-dir ".\哔哩动画"
    )
    echo echo 下载完成
    echo pause
) > "!OUT_FILE!"
del _temp_quality.txt 2>nul

echo [3/3] 已生成: !OUT_FILE!
echo 分发时一起带走: 本bat + BBDown.exe + BBDownTV.data(TV模式) + ffmpeg.exe + aria2c.exe(可选)
echo.
echo ========================================
echo  继续输入下一个链接, Ctrl+C 退出
echo ========================================
echo.
goto AskURL

:LoginTV
echo.
echo 正在启动 TV 端扫码登录...
pushd "%~dp0"
"%~dp0BBDown.exe" logintv
set "LOGIN_RC=!errorlevel!"
popd
if not "!LOGIN_RC!"=="0" (
    echo [错误] TV 端扫码登录未完成
    echo.
    goto SelectMode
)
set "TV_ACCESS_TOKEN="
if exist "%~dp0BBDownTV.data" for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0BBDownTV.data") do if /I "%%A"=="access_token" set "TV_ACCESS_TOKEN=%%B"
if not defined TV_ACCESS_TOKEN (
    echo [错误] 登录命令结束，但没有生成有效 BBDownTV.data
    echo.
    goto SelectMode
)
echo TV 端登录成功，BBDownTV.data 已更新
echo.
goto SelectMode

:LoginWEB
echo.
echo 正在启动 WEB 端扫码登录...
if not exist "%~dp0BBDown_login_fixed.exe" (
    echo [错误] 缺少 BBDown_login_fixed.exe
    echo.
    goto SelectMode
)
pushd "%~dp0"
"%~dp0BBDown_login_fixed.exe" login
set "LOGIN_RC=!errorlevel!"
popd
if not "!LOGIN_RC!"=="0" (
    echo [错误] WEB 端扫码登录未完成
    echo.
    goto SelectMode
)
if not exist "%~dp0BBDown.data" (
    echo [错误] 登录命令结束，但没有生成 BBDown.data
    echo.
    goto SelectMode
)
findstr /C:"SESSDATA=" "%~dp0BBDown.data" >nul
if errorlevel 1 (
    echo [错误] BBDown.data 中没有有效 SESSDATA
    echo.
    goto SelectMode
)
echo WEB 端登录成功，BBDown.data 已更新
echo.
goto SelectMode

:End
echo.
echo 已退出
exit /b 0
'''

out = Path(__file__).with_name("哔哩统一下载.bat")
out.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("gbk"))
print("wrote", out, out.stat().st_size)
