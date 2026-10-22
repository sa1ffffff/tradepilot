@echo off
rem Double-click to open the Tradepilot dashboard. Close this window to stop it.
cd /d "%~dp0"
".venv\Scripts\python.exe" dashboard.py
pause
