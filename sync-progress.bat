@echo off
setlocal
if "%~1"=="" (
  echo Usage: sync-progress.bat "C:\\path\\to\\context-lab-progress-YYYY-MM-DD.json"
  echo Export the sync record from Context Lab first, then pass its path here.
  exit /b 2
)
python "%~dp0tools\\desktop_sync.py" push "%~1"
if errorlevel 1 pause
