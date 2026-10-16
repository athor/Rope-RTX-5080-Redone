@echo off
setlocal
cd /d "%~dp0"
call "%~dp0venv\Scripts\activate.bat"
"%~dp0venv\Scripts\python.exe" Rope.py
pause
endlocal
