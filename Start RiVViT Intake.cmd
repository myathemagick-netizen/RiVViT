@echo off
setlocal
cd /d "%~dp0"
set "RIVVIT_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%RIVVIT_PYTHON%" (
  "%RIVVIT_PYTHON%" tools\serve_intake.py --open-browser %*
  goto finished
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 tools\serve_intake.py --open-browser %*
  goto finished
)
echo Python 3 was not found. Run tools\serve_intake.py with an available Python 3 interpreter.
:finished
echo.
echo Saved intake data remains in the local workspace. Keep the serving window open while reviewing.
pause
