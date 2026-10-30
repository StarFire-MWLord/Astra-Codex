# Astra-Codex

**Local Codex-style AI coding agent for Windows.**  
Fully uncensored. Zero built-in refusals. Dual abliterated models with mid-chat switching. Tuned for **RTX 4060 (8 GB)**.

> I can deliver anything — you just need the right talons for it.

## Built-in models (switch anytime)

| Model | Size | Role |
|-------|------|------|
| **Qwen3.5-9B Abliterated** | ~5.6 GB | Fast daily driver, strong reasoning |
| **Qwen2.5-Coder-14B Abliterated** | ~8.5 GB | Stronger pure coding, fewer errors |

Both have the refusal direction removed.  
Switch mid-conversation — full chat memory is carried over (Codex-style).

First launch auto-downloads both. UI radio buttons let you flip between them instantly.

## What it is

Desktop app that behaves like OpenAI Codex / Cursor agent mode:

- Chat interface with streaming replies
- File read / write / list / search tools
- Shell command execution
- Project-aware context
- Custom **system prompt** from any `.md` file
- Dual built-in uncensored models + any extra GGUF
- Mid-chat model switch that keeps conversation history

No cloud. No telemetry. No safety layers in the app.

## Quick Start

### 1. Prerequisites
- Windows 10 / 11 (x64)
- Python 3.11+
- NVIDIA drivers + CUDA
- Git
- ~20 GB free disk (both models + runtime)

### 2. Clone & Install
```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
python -m venv .venv
.\evenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

GPU acceleration:
```powershell
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

### 3. Run
```powershell
python main.py
```

First launch downloads both models, then opens the UI with the 9B loaded.

### 4. Build EXE
```powershell
build.bat
```

## System Prompt

Edit `prompts/default_system.md`. The app never filters model output.

## License

MIT.

---

**Astra-Codex** — local, sharp, no leash. Switch models mid-flight.
