@echo off
echo Building Macro Malware Suite...
echo.

REM Install dependencies
pip install -r requirements.txt

REM Run the application
python macro.py

pause
