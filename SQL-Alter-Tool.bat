@echo off
setlocal
cd /d "%~dp0"

set "PY="
set "PYVER=3.12"
set "PYDIR=%LocalAppData%\Programs\Python\Python312"

:: 1. Find Python (prefer the py launcher; the Windows Store "python" stub is unreliable)
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY if exist "%PYDIR%\python.exe" set "PY="%PYDIR%\python.exe""

:: 2. Install Python if missing (per-user, no admin needed)
if not defined PY (
    echo Python not found. Installing Python %PYVER%...
    winget install -e --id Python.Python.%PYVER% --scope user --silent --accept-package-agreements --accept-source-agreements
    if exist "%PYDIR%\python.exe" (
        set "PY="%PYDIR%\python.exe""
    ) else (
        echo Python install failed. Please install Python %PYVER% manually from python.org.
        pause
        exit /b 1
    )
)

:: 3. Create venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY% -m venv .venv || (echo venv creation failed & pause & exit /b 1)
)

:: 4. Install requirements only if requirements.txt changed
fc /b requirements.txt .venv\requirements.installed >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || (echo pip install failed & pause & exit /b 1)
    copy /y requirements.txt .venv\requirements.installed >nul
)

:: 5. Run the app (no console window)
start "" ".venv\Scripts\pythonw.exe" src\gui.py
exit /b 0
