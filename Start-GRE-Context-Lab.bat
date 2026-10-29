@echo off
setlocal EnableExtensions
title GRE Context Lab Launcher

set "REPO_URL=https://github.com/VMoonAuraV/backup-04.git"
set "TARGET=%LOCALAPPDATA%\GRE-Context-Lab\backup-04"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git for Windows is not installed or not on PATH.
  echo Install Git from https://git-scm.com/download/win, then double-click this file again.
  pause
  exit /b 1
)

where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python 3 is not installed or not on PATH.
    echo Install Python 3 from https://www.python.org/downloads/windows/
    echo During installation, enable "Add python.exe to PATH".
    pause
    exit /b 1
  )
  set "PYTHON_LAUNCHER=python"
) else (
  set "PYTHON_LAUNCHER=py -3"
)

rem If this file was launched from a ZIP, clone a Git working copy first.
if not exist "%~dp0.git" (
  if exist "%TARGET%\.git" (
    echo Using existing working copy: %TARGET%
    cd /d "%TARGET%"
    goto run_app
  )
  if exist "%TARGET%" (
    echo [ERROR] The target folder exists but is not a Git repository:
    echo %TARGET%
    echo Please rename that folder or remove it after checking its contents.
    pause
    exit /b 1
  )
  if not exist "%LOCALAPPDATA%\GRE-Context-Lab" mkdir "%LOCALAPPDATA%\GRE-Context-Lab"
  echo First launch: cloning the learning system to:
  echo %TARGET%
  git clone "%REPO_URL%" "%TARGET%"
  if errorlevel 1 (
    echo [ERROR] Could not clone the repository. Check your network and Git installation.
    pause
    exit /b 1
  )
  cd /d "%TARGET%"
) else (
  cd /d "%~dp0"
)

:run_app
if not exist "tools\desktop_app.py" (
  echo [ERROR] Cannot find tools\desktop_app.py in:
  echo %CD%
  pause
  exit /b 1
)

echo.
echo Starting GRE Context Lab...
echo A browser tab will open automatically.
echo Keep this window open while studying.
echo Website: http://127.0.0.1:8765/
echo Repository: %CD%
echo Press Ctrl+C to stop the local server.
echo.

if "%PYTHON_LAUNCHER%"=="python" (
  python tools\desktop_app.py
) else (
  py -3 tools\desktop_app.py
)

if errorlevel 1 (
  echo.
  echo [ERROR] GRE Context Lab stopped with an error.
  echo Please send the error text above for diagnosis.
  pause
)
