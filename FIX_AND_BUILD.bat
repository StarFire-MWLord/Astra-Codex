@echo off
setlocal EnableDelayedExpansion
title Astra-Codex Fix and Build
color 0B

set LOG=%~dp0fix_build.log
echo [%date% %time%] Starting FIX_AND_BUILD > "%LOG%"

echo ============================================
echo   Astra-Codex Fix and Build
echo   Forces Python 3.12 + CUDA llama + clean EXE
echo ============================================
echo.
echo Log: %LOG%
echo.

:: Find or install Python 3.12
echo Looking for Python 3.12...
echo Looking for Python 3.12... >> "%LOG%"
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.12 not found. Downloading installer with curl...
    echo Downloading Python 3.12 with curl... >> "%LOG%"
    curl -L -o python-3.12.7-amd64.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe >> "%LOG%" 2>&1
    if not exist python-3.12.7-amd64.exe (
        echo Download failed. Check internet.
        echo Download failed. >> "%LOG%"
        type "%LOG%"
        pause
        exit /b 1
    )
    echo Download finished. Installing Python 3.12...
    echo Installing Python 3.12... >> "%LOG%"
    start /wait python-3.12.7-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 /log python_install.log
    del python-3.12.7-amd64.exe
    echo.
    echo Python 3.12 installed.
    echo Close this window and run FIX_AND_BUILD.bat again so PATH updates.
    echo Restart required for PATH. >> "%LOG%"
    pause
    exit /b 0
)
echo     Found Python 3.12
echo Found Python 3.12 >> "%LOG%"

:: Kill old venv
echo.
echo Removing old .venv...
echo Removing .venv... >> "%LOG%"
if exist .venv (
    rmdir /s /q .venv
)

:: Fresh venv with 3.12
echo Creating fresh .venv with Python 3.12...
echo Creating venv... >> "%LOG%"
py -3.12 -m venv .venv >> "%LOG%" 2>&1
if errorlevel 1 (
    echo Failed to create venv
    echo venv failed. >> "%LOG%"
    type "%LOG%"
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo Upgrading pip...
echo Upgrading pip... >> "%LOG%"
python -m pip install --upgrade pip --quiet >> "%LOG%" 2>&1

:: Core packages
echo.
echo Installing requirements...
echo Installing requirements... >> "%LOG%"
pip install -r requirements.txt --quiet >> "%LOG%" 2>&1

:: CUDA llama-cpp-python
echo.
echo Installing CUDA llama-cpp-python...
echo Installing llama-cpp-python CUDA... >> "%LOG%"
pip uninstall llama-cpp-python -y >nul 2>&1
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --quiet >> "%LOG%" 2>&1
if errorlevel 1 (
    echo CUDA wheel failed. Falling back to CPU.
    echo CUDA failed, CPU fallback. >> "%LOG%"
    pip install llama-cpp-python --quiet >> "%LOG%" 2>&1
)

:: Test the import
echo.
echo Testing llama_cpp import...
echo Testing import... >> "%LOG%"
python -c "from llama_cpp import Llama; print('llama_cpp loads clean')" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo Import failed. DLL problem remains.
    echo Import failed. >> "%LOG%"
    type "%LOG%"
    pause
    exit /b 1
)
echo llama_cpp loads clean

:: Pull latest
echo.
echo Pulling latest from repo...
echo git pull... >> "%LOG%"
git stash --include-untracked >nul 2>&1
git pull >> "%LOG%" 2>&1

:: Clean old builds
echo.
echo Cleaning dist and build...
echo Cleaning dist/build... >> "%LOG%"
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Build with the spec
echo.
echo Building EXE with Astra-Codex.spec...
echo Building EXE... >> "%LOG%"
pyinstaller --noconfirm Astra-Codex.spec >> "%LOG%" 2>&1
if not exist "dist\Astra-Codex.exe" (
    echo Build failed.
    echo Build failed. >> "%LOG%"
    type "%LOG%"
    pause
    exit /b 1
)

:: Portable package
echo.
echo Making portable package...
echo Portable package... >> "%LOG%"
if not exist "dist\models" mkdir "dist\models"
if not exist "dist\prompts" mkdir "dist\prompts"
xcopy /y /q "models\*.gguf" "dist\models\" >nul 2>&1
xcopy /y /q /e "prompts\*" "dist\prompts\" >nul 2>&1

:: Shortcut
echo.
echo Creating desktop shortcut...
echo Shortcut... >> "%LOG%"
set "EXE=%CD%\dist\Astra-Codex.exe"
set "DESKTOP=C:\Users\Administrator\Desktop"
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\Astra-Codex.lnk'); $s.TargetPath = '%EXE%'; $s.WorkingDirectory = '%CD%\dist'; $s.Description = 'Astra-Codex'; $s.Save()" >> "%LOG%" 2>&1

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
echo Done. >> "%LOG%"
pause
