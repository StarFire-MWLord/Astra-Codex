@echo off
setlocal EnableDelayedExpansion
title Astra-Codex Fix and Build
color 0B

echo ============================================
echo   Astra-Codex Fix and Build
echo   Forces Python 3.12 + CUDA llama + clean EXE
echo ============================================
echo.

:: Find Python 3.12
echo Looking for Python 3.12...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.12 not found.
    echo Install it from https://www.python.org/downloads/release/python-3120/
    echo Check "Add python.exe to PATH" during install.
    echo Then run this bat again.
    pause
    exit /b 1
)
echo     Found Python 3.12

:: Kill old venv
echo.
echo Removing old .venv...
if exist .venv (
    rmdir /s /q .venv
)

:: Fresh venv with 3.12
echo Creating fresh .venv with Python 3.12...
py -3.12 -m venv .venv
if errorlevel 1 (
    echo Failed to create venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Core packages
echo.
echo Installing requirements...
pip install -r requirements.txt --quiet

:: CUDA llama-cpp-python
echo.
echo Installing CUDA llama-cpp-python...
pip uninstall llama-cpp-python -y >nul 2>&1
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --quiet
if errorlevel 1 (
    echo CUDA wheel failed. Falling back to CPU.
    pip install llama-cpp-python --quiet
)

:: Test the import
echo.
echo Testing llama_cpp import...
python -c "from llama_cpp import Llama; print('llama_cpp loads clean')"
if errorlevel 1 (
    echo Import failed. DLL problem remains.
    pause
    exit /b 1
)

:: Pull latest (ignore untracked for now)
echo.
echo Pulling latest from repo...
git stash --include-untracked >nul 2>&1
git pull

:: Clean old builds
echo.
echo Cleaning dist and build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build with the spec
echo.
echo Building EXE with Astra-Codex.spec...
pyinstaller --noconfirm Astra-Codex.spec
if not exist "dist\Astra-Codex.exe" (
    echo Build failed.
    pause
    exit /b 1
)

:: Portable package
echo.
echo Making portable package...
if not exist "dist\models" mkdir "dist\models"
if not exist "dist\prompts" mkdir "dist\prompts"
xcopy /y /q "models\*.gguf" "dist\models\" >nul 2>&1
xcopy /y /q /e "prompts\*" "dist\prompts\" >nul 2>&1

:: Shortcut (fixed escaping)
echo.
echo Creating desktop shortcut...
set "EXE=%CD%\dist\Astra-Codex.exe"
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\Astra-Codex.lnk'); $s.TargetPath = '%EXE%'; $s.WorkingDirectory = '%CD%\dist'; $s.Description = 'Astra-Codex'; $s.Save()"

echo.
echo ============================================
echo   DONE
echo ============================================
echo.
echo   EXE: dist\Astra-Codex.exe
echo   Models copied next to it.
echo.
echo   Double-click the EXE or the desktop shortcut.
echo.
pause
