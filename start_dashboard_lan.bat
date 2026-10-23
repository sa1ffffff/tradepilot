@echo off
rem Opens the Tradepilot console for this PC AND your phone on the same Wi-Fi.
rem The window prints a private link with a token: open that on the phone.
rem Windows may ask to allow Python through the firewall: allow it on Private networks only.
cd /d "%~dp0"
".venv\Scripts\python.exe" dashboard.py --lan
pause
