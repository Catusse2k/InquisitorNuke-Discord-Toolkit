@echo off
cd /d "%~dp0"
where python >nul 2>nul && (python setup.py) || (call setup_fallback.bat)
pause