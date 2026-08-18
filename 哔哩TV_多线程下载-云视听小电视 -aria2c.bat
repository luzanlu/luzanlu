@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
TITLE 哔哩TV_多线程下载-云视听小电视 (集成Aria2引擎版)
color 0A

echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo ┃                      请输入以下选项序列号，回车键确定                      ┃
echo ┃                                                                            ┃
echo ┃                      模式：TV                                              ┃
echo ┃                      程序版本：BBDown_1.5.8_20230608                       ┃
echo ┃                                                                            ┃
echo ┃                      哔哩TV_下载-更新：2022年6月8日                        ┃
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo ┃       0：哔哩TV_下载-自定义集数 (仅选一次画质，后续全自动)                 ┃
echo ┃       00：哔哩TV_解析-自定义集数                                           ┃                               
echo ┃  ——————————————————————————————————————— ┃
echo ┃       1：哔哩TV_下载-ia-最新集数                                           ┃
echo ┃       2：哔哩TV_下载-自定义集数-1080p高码-HEVC                             ┃
echo ┃       3：哔哩TV_解析-最新集数                                              ┃
echo ┃       4：哔哩TV_下载-自定义集数-1080p高码-AVC                              ┃
echo ┃       5：哔哩TV_下载-全部集数 (仅选一次画质，后续全自动)                   ┃
echo ┃                                                                            ┃
echo ┃       6：【推荐】智能解析列表，按序号指定画质，可选 Aria2 引擎全自动下载   ┃
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

set /p user_input=请输入菜单数字：
set /p URL=请输入视频地址 或 AV/BV/EP/SS：
echo.

if "%user_input%"=="" (
    echo 【错误】没有输入菜单数字，请重新打开脚本后选择 0、00、1、2、3、4、5 或 6。
    goto notice
)
if "%URL%"=="" (
    echo 【错误】视频地址不能为空。
    echo 示例：https://www.bilibili.com/bangumi/play/ss45962
    goto notice
)

if "%user_input%"=="0" (
    set /p jishu=请输入视频集数 [例如 1-5、8、1,2,3、LAST]：
    if "!jishu!"=="" (
        echo 【错误】集数不能为空。示例：1、1-5、1,2,3、LAST。
        goto notice
    )
    goto AutoStreamDownload
)
if "%user_input%"=="00" goto ParseCustom
if "%user_input%"=="1" goto DownloadIaLast
if "%user_input%"=="2" goto DownloadCustomHEVC
if "%user_input%"=="3" goto ParseLast
if "%user_input%"=="4" goto DownloadCustomAVC
if "%user_input%"=="5" (
    set "jishu=ALL"
    goto AutoStreamDownload
)
if "%user_input%"=="6" goto SmartDownload

echo 【错误】无效菜单数字：%user_input%
echo 请重新打开脚本，只输入菜单中显示的数字。
goto notice

:: ==========================================
:: 公共批量下载模块 (处理选项 0 和 5 的免打扰下载)
:: ==========================================
:AutoStreamDownload
call :AskEngine
echo.
echo [1/3] 正在探测视频可用画质，请稍候...
BBDown -tv -info "%URL%" -p 1 > temp_info.txt

echo.
echo =========================================================================
echo 提取到的可用视频流如下 (音轨将全自动匹配最高配置)：
echo -------------------------------------------------------------------------
set "v_count=0"
for /f "tokens=1,2,3,4 delims=[]" %%A in ('type temp_info.txt ^| findstr /I /C:"AVC" /C:"HEVC" /C:"AV1"') do (
    echo   [!v_count!] 画质: %%B  丨  编码: %%D
    set "val_dfn_!v_count!=%%B"
    set "val_enc_!v_count!=%%D"
    set /a v_count+=1
)
echo =========================================================================

if !v_count!==0 (
    echo 【错误】未能成功抓取视频流。可能网络超时，或该视频需要登录/权限。
    echo 为避免下错画质，本次不自动下载。请先用解析模式确认可用流。
    del temp_info.txt 2>nul
    goto notice
)

:PickAutoStream
set /p sel_idx="[2/3] 请输入视频流序号（只输入左侧数字，例如 0 或 1）："
set "target_dfn=!val_dfn_%sel_idx%!"
set "target_enc=!val_enc_%sel_idx%!"

if "!target_dfn!"=="" (
    echo 【错误】没有这个序号，请输入列表左侧的数字。
    goto PickAutoStream
)

echo.
echo 确认选择 =^> 画质: [!target_dfn!]，编码: [!target_enc!]
del temp_info.txt 2>nul

echo.
echo [3/3] 正在启动全自动免打扰下载...
BBDown -tv --skip-cover "%URL%" -p %jishu% --dfn-priority "!target_dfn!" --encoding-priority "!target_enc!" %EXTRA_CMD% --work-dir .\哔哩动画
goto notice
:: ==========================================


:ParseCustom
set /p jishu=请输入视频集数 [例如 1、1-5、LAST]：
if "%jishu%"=="" (
    echo 【错误】集数不能为空。
    goto notice
)
BBDown -tv -info "%URL%" -p %jishu%
goto notice

:DownloadIaLast
call :AskEngine
BBDown -tv -ia --skip-cover "%URL%" -p LAST %EXTRA_CMD% --work-dir .\哔哩动画
goto notice

:DownloadCustomHEVC
set /p jishu=请输入视频集数 [例如 1、1-5、LAST]：
if "%jishu%"=="" (
    echo 【错误】集数不能为空。
    goto notice
)
call :AskEngine
BBDown -tv --skip-cover "%URL%" -p %jishu% --encoding-priority "hevc,avc,av1" --dfn-priority "1080P 高码率" %EXTRA_CMD% --work-dir .\哔哩动画
goto notice

:ParseLast
BBDown -tv -info "%URL%" -p LAST
goto notice

:DownloadCustomAVC
set /p jishu=请输入视频集数 [例如 1、1-5、LAST]：
if "%jishu%"=="" (
    echo 【错误】集数不能为空。
    goto notice
)
call :AskEngine
BBDown -tv --skip-cover "%URL%" -p %jishu% --encoding-priority "avc,hevc,av1" --dfn-priority "1080P 高码率" %EXTRA_CMD% --work-dir .\哔哩动画
goto notice

:SmartDownload
echo.
echo [1/4] 正在探测该视频第一集的可用视频流，请稍候...
BBDown -tv -info "%URL%" -p 1 > temp_info.txt

echo.
echo =========================================================================
echo 提取到的可用视频流如下 (音轨将全自动匹配最高配置)：
echo -------------------------------------------------------------------------
set "v_count=0"
for /f "tokens=1,2,3,4 delims=[]" %%A in ('type temp_info.txt ^| findstr /I /C:"AVC" /C:"HEVC" /C:"AV1"') do (
    echo   [!v_count!] 画质: %%B  丨  编码: %%D
    set "val_dfn_!v_count!=%%B"
    set "val_enc_!v_count!=%%D"
    set /a v_count+=1
)
echo =========================================================================

if !v_count!==0 (
    echo 【错误】未能成功抓取视频流。可能网络超时，或该视频格式特殊。
    del temp_info.txt 2>nul
    goto notice
)

:PickSmartStream
set /p sel_idx="[2/4] 请输入视频流序号（只输入左侧数字，例如 0 或 1）："
set "target_dfn=!val_dfn_%sel_idx%!"
set "target_enc=!val_enc_%sel_idx%!"

if "!target_dfn!"=="" (
    echo 【错误】没有这个序号，请输入列表左侧的数字。
    goto PickSmartStream
)

echo.
echo 确认选择 =^> 画质: [!target_dfn!]，编码: [!target_enc!]
del temp_info.txt 2>nul

echo.
echo [3/4] 关键设置：请选择下载引擎与线程策略
echo [提示] B站服务器经常拦截默认的多线程请求，建议根据实际情况选择：
echo   1. BBDown 自带多线程 (速度快，但部分视频易报"不支持多线程"错误)
echo   2. BBDown 单线程模式 (速度较慢，但最稳定不报错)
echo   3. 强力引擎 Aria2c 多线程 (速度极快且抗拦截，前提：目录下必须有 aria2c.exe)
set /p engine_choice="请输入策略序号 (1/2/3，直接回车默认选3): "

if "%engine_choice%"=="" set "engine_choice=3"

set "EXTRA_CMD="
if "%engine_choice%"=="1" (
    echo 【已选择: BBDown 默认多线程】
) else if "%engine_choice%"=="2" (
    echo 【已选择: 单线程防风控模式】
    set "EXTRA_CMD=--multi-thread false"
) else if "%engine_choice%"=="3" (
    echo 【已选择: Aria2c 多线程强力引擎】
    set "EXTRA_CMD=--use-aria2c"
) else (
    echo 【提示】输入无效，已按默认策略选择 Aria2c 多线程强力引擎。
    set "EXTRA_CMD=--use-aria2c"
)

echo.
echo [4/4] 正在启动全集下载...
BBDown -tv --skip-cover "%URL%" -p ALL --dfn-priority "!target_dfn!" --encoding-priority "!target_enc!" %EXTRA_CMD% --work-dir .\哔哩动画
goto notice


:: ==========================================
:: 二级菜单子程序：选择下载引擎
:: ==========================================
:AskEngine
echo.
echo --------------------------------------------------
echo 请选择下载引擎 (二级菜单)：
echo   1. 默认下载引擎 (BBDown自带)
echo   2. 使用 Aria2c 下载 (调用aria2c进行下载，需自行准备好二进制可执行文件)
echo --------------------------------------------------
set /p engine_choice="请输入选项 (1 或 2，直接回车默认选1): "
if "%engine_choice%"=="" set "engine_choice=1"
set "EXTRA_CMD="
if "%engine_choice%"=="2" (
    set "EXTRA_CMD=--use-aria2c"
    echo 【已选择: Aria2c 下载引擎】
) else if "%engine_choice%"=="1" (
    echo 【已选择: 默认下载引擎】
) else (
    echo 【提示】输入无效，已默认使用 BBDown 自带下载引擎。
)
goto :EOF
:: ==========================================


:notice
echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo  ————————————————————————————————————————————————————————————————————————————
echo  ———————————————————————————————请按任意键退出———————————————————————————————
echo  ————————————————————————————————————————————————————————————————————————————
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

echo.
pause