@echo off
echo Building Astra-Codex.exe with llama_cpp libs bundled...
pip install pyinstaller customtkinter llama-cpp-python pillow
pyinstaller --noconfirm Astra-Codex.spec
echo.
echo Done. EXE is in dist\Astra-Codex.exe
echo Put your .gguf models in a models\ folder next to the EXE.
pause
