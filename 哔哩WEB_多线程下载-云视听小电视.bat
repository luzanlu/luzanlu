@echo off
TITLE 哔哩WEB_多线程下载-云视听小电视
color 0A
:: 2023年4月7日

echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo ┃                      请输入以下选项序列号，回车键确定                      ┃
echo ┃                                                                            ┃
echo ┃                      模式：WEB                                              ┃
echo ┃                      程序版本：BBDown_1.5.8_20230608                       ┃
echo ┃                                                                            ┃
echo ┃                      哔哩WEB_下载-更新：2022年6月8日                        ┃
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo ┃       0：哔哩WEB_下载-ia-自定义集数                                         ┃
echo ┃                                                                            ┃
echo ┃       00：哔哩WEB_解析-自定义集数                                           ┃                                  
echo ┃                                                                            ┃ 
echo  ———————————————————————————————————————
echo ┃                                                                            ┃
echo ┃       1：哔哩WEB_下载-ia-最新集数                                           ┃
echo ┃                                                                            ┃
echo ┃                                                                            ┃
echo ┃       2：哔哩WEB_下载-自定义集数-1080p高码-HEVC                             ┃
echo ┃                                                                            ┃
echo ┃                                                                            ┃
echo ┃       3：哔哩WEB_解析-最新集数                                              ┃
echo ┃                                                                            ┃
echo ┃                                                                            ┃
echo ┃       4：哔哩WEB_下载-自定义集数-1080p高码-AVC                              ┃
echo ┃                                                                            ┃
echo ┃                                                                            ┃
echo ┃       5：哔哩WEB_下载-最高质量-全部集数                                           ┃
echo ┃
echo ┃       6：哔哩TV_下载-最高质量-自定义集数                                           ┃
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

set /p user_input=请输入数字：
set /p URL= 请输入视频地址 或 AV丨BV丨EP丨SS：
echo.

if "%user_input%"=="0" goto 哔哩WEB_下载-ia-自定义
if "%user_input%"=="00" goto 哔哩WEB_解析-自定义
if "%user_input%"=="1" goto 哔哩WEB_下载-ia-最新集数
if "%user_input%"=="2" goto 哔哩WEB_下载-自定义集数-1080p高码-HEVC
if "%user_input%"=="3" goto 哔哩WEB_解析-最新集数
if "%user_input%"=="4" goto 哔哩WEB_下载-自定义集数-1080p高码-AVC
if "%user_input%"=="5" goto 哔哩WEB_下载-ia-全部集数
if "%user_input%"=="6" goto 哔哩TV_下载-最高质量-自定义集数 


:哔哩WEB_下载-ia-自定义
set /p jishu= 请输入视频集数 [选择集数请输入1-999]：
BBDown -ia --skip-cover %URL% --work-dir .\哔哩动画 --video-only --audio-only -p %jishu%
goto notice

:哔哩WEB_解析-自定义
set /p jishu= 请输入视频集数 [选择集数请输入1-999]：
BBDown -info %URL% -p %jishu%
goto notice

:哔哩WEB_下载-ia-最新集数
BBDown -ia --use-aria2c --skip-cover %URL% -p LAST --work-dir .\哔哩动画
goto notice

:哔哩WEB_下载-自定义集数-1080p高码-HEVC
set /p jishu= 请输入视频集数 [选择集数请输入1-999]：
BBDown --skip-cover %URL% -p %jishu% --encoding-priority "hevc,avc,av1" --dfn-priority "1080P 高码率" --work-dir .\哔哩动画
goto notice

:哔哩WEB_解析-最新集数
BBDown -info %URL% -p LAST
goto notice

:哔哩WEB_下载-自定义集数-1080p高码-AVC
set /p jishu= 请输入视频集数 [选择集数请输入1-999]：
BBDown -WEB --skip-cover %URL% -p %jishu% --encoding-priority "avc,hevc,av1" --dfn-priority "1080P 高码率" --work-dir .\哔哩动画
goto notice

:哔哩WEB_下载-ia-全部集数
BBDown --skip-cover %URL% -p ALL --work-dir .\哔哩动画
goto notice

:哔哩TV_下载-最高质量-自定义集数 
BBDown -tv -cover %URL% -p %jishu%
goto notice

:notice

echo ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
echo  ————————————————————————————————————————————————————————————————————————————
echo  ———————————————————————————————请按任意键退出———————————————————————————————
echo  ————————————————————————————————————————————————————————————————————————————
echo ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

echo.
pause