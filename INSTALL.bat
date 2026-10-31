@echo off
setlocal EnableDelayedExpansion
title Astra-Codex Installer
color 0B

echo ============================================
echo   Astra-Codex Smart Installer
echo   Uncensored local Codex for RTX 4060
echo ============================================
echo.

:: ------------------------------------------------
:: 1. Check Python
:: ------------------------------------------------
echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.11+ from python.org
    echo Make sure to check "Add python.exe to PATH"
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo     Found Python %PYVER%

:: ------------------------------------------------
:: 2. Create / reuse virtual environment
:: ------------------------------------------------
echo [2/7] Virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo     .venv already exists — reusing
) else (
    echo     Creating .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create venv
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat

:: ------------------------------------------------
:: 3. Install / update Python packages (skip if present)
:: ------------------------------------------------
echo [3/7] Python packages...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo     Installing requirements...
    pip install -r requirements.txt --quiet
) else (
    echo     Core packages already present — skipping full reinstall
    pip install -r requirements.txt --quiet --upgrade
)

:: Force CUDA build of llama-cpp-python if possible
echo     Ensuring CUDA llama-cpp-python...
pip uninstall llama-cpp-python -y >nul 2>&1
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --quiet
if errorlevel 1 (
    echo     CUDA wheel failed — falling back to CPU build
    pip install llama-cpp-python --quiet
)

:: ------------------------------------------------
:: 4. Download both abliterated models (skip if exist)
:: ------------------------------------------------
echo [4/7] Models...
if not exist "models" mkdir models

python -c "from core.model_bootstrap import ensure_default_models; ensure_default_models('models')"
if errorlevel 1 (
    echo     Model download had issues — you can retry later from the app
) else (
    echo     Models ready
)

:: ------------------------------------------------
:: 5. Install PyInstaller if needed
:: ------------------------------------------------
echo [5/7] PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    pip install pyinstaller --quiet
) else (
    echo     PyInstaller already present
)

:: ------------------------------------------------
:: 6. Build the EXE
:: ------------------------------------------------
echo [6/7] Building Astra-Codex.exe ...
if exist "dist\Astra-Codex.exe" (
    echo     Removing old EXE...
    del /q "dist\Astra-Codex.exe"
)

pyinstaller --noconfirm Astra-Codex.spec

if not exist "dist\Astra-Codex.exe" (
    echo Build failed.
    pause
    exit /b 1
)
echo     EXE built successfully

:: Copy models + prompts next to the EXE so it is portable
echo     Making portable package...
if not exist "dist\models" mkdir "dist\models"
if not exist "dist\prompts" mkdir "dist\prompts"
xcopy /y /q "models\*.gguf" "dist\models\" >nul 2>&1
xcopy /y /q /e "prompts\*" "dist\prompts\" >nul 2>&1

:: ------------------------------------------------
:: 7. Desktop shortcut
:: ------------------------------------------------
echo [7/7] Desktop shortcut...
set "EXE=%CD%\dist\Astra-Codex.exe"
set "DESKTOP=C:\Users\Administrator\Desktop"

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut('%DESKTOP%\Astra-Codex.lnk'); ^
   $s.TargetPath = '%EXE%'; ^
   $s.WorkingDirectory = '%CD%\dist'; ^
   $s.Description = 'Astra-Codex - Local Uncensored Coding Agent'; ^
   $s.Save()"

echo.
echo ============================================
echo   INSTALL COMPLETE
echo ============================================
echo.
echo   EXE location : dist\Astra-Codex.exe
echo   Desktop shortcut created: Astra-Codex
echo.
echo   Double-click the desktop icon to launch.
echo   First run will use the models already downloaded.
echo.
pause
