@echo off
chcp 65001 > nul
echo 正在启动OCR识别程序...
python moto_ocr.py
echo 处理完成！
pause
