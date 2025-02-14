@echo off
cd /d %~dp0
echo Starting Zygo Monitor Service...

:start
python start_monitor.py
if errorlevel 1 (
    echo Service stopped with error code %errorlevel%
    echo Restarting in 60 seconds...
    timeout /t 60
    goto start
)
pause