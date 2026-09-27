@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; assert sys.version_info >= (3,10)" >nul 2>nul
  if not errorlevel 1 goto use_py
)
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; assert sys.version_info >= (3,10)" >nul 2>nul
  if not errorlevel 1 goto use_python
)
echo Install Python 3.10 or newer from https://www.python.org/downloads/
echo Enable Add Python to PATH, then run start.bat again.
echo Help: docs/USER_GUIDE_JA.md or docs/USER_GUIDE_EN.md
pause
exit /b 1
:use_py
py -3 bootstrap.py
goto done
:use_python
python bootstrap.py
:done
if errorlevel 1 pause
