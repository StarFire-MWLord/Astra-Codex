@echo off
echo Building Astra-Codex.exe ...
pip install pyinstaller customtkinter llama-cpp-python pillow
pyinstaller --noconfirm --onefile --windowed --name Astra-Codex --add-data "prompts;prompts" main.py
echo.
echo Done. EXE is in dist\Astra-Codex.exe
echo Put your .gguf models in a models\ folder next to the EXE.
pause
