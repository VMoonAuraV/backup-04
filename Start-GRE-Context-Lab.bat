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
  set "PYTHON_CMD=python"
) else (
  set "PYTHON_CMD=py -3"
)

rem If launched from a ZIP download, clone a Git working copy so syncing can work.
if not exist "%~dp0.git" (
  if exist "%TARGET%\.git" (
    call "%TARGET%\Start-GRE-Context-Lab.bat"
    exit /b
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
  call "%TARGET%\Start-GRE-Context-Lab.bat"
  exit /b
)

cd /d "%~dp0"
if not exist "tools\desktop_app.py" (
  echo [ERROR] Cannot find tools\desktop_app.py in this repository.
  pause
  exit /b 1
)

echo Starting GRE Context Lab...
echo A browser tab will open automatically.
echo Keep the server window open while studying.
echo.
if "%PYTHON_CMD%"=="python" (
  start "GRE Context Lab - local server" "%ComSpec%" /k "cd /d ""%~dp0"" && python tools\desktop_app.py"
) else (
  start "GRE Context Lab - local server" "%ComSpec%" /k "cd /d ""%~dp0"" && py -3 tools\desktop_app.py"
)
exit /b 0
