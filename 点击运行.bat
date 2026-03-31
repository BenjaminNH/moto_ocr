@echo off
chcp 65001 > nul
echo 正在启动OCR识别程序...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请确认已安装并添加到 PATH
    pause
    exit /b 1
)

python -m moto_ocr.main
if %errorlevel% neq 0 (
    echo [错误] 程序运行失败，错误码：%errorlevel%
    pause
    exit /b %errorlevel%
)

echo 处理完成！
pause
