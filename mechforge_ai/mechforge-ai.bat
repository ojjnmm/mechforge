@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d E:\
"E:\Environments\Python\python.exe" "E:\mechforge_ai\run_main.py" %*
