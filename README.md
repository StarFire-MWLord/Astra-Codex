# Astra-Codex

**Local Codex-style AI coding agent for Windows.**  
Fully uncensored. Zero built-in refusals. Ships with a strong default **abliterated** model. Tuned for **RTX 4060 (8 GB)**.

> I can deliver anything — you just need the right talons for it.

## Built-in model (smarter default)

On first launch the app automatically downloads and loads:

**Huihui-Qwen3.5-9B-abliterated (Q4_K_M)**  
~5.6 GB · comfortable on RTX 4060 8 GB  
Source: `mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF`

This is a step up from the previous 7B default: better reasoning, better instruction following, still fully abliterated (refusal direction removed). Good fit for C++ work, reverse-engineering style tasks, Frida scripts, mod menus, and agent-style coding.

You can still drop any other GGUF into `models/` later.

## What it is

Desktop app that behaves like OpenAI Codex / Cursor agent mode:

- Chat interface with streaming replies
- File read / write / list / search tools
- Shell command execution
- Project-aware context
- Custom **system prompt** from any `.md` file
- GGUF backend (llama.cpp) with full GPU offload
- First-run auto-download of the default uncensored model

No cloud. No telemetry. No safety layers in the app.

## Quick Start

### 1. Prerequisites
- Windows 10 / 11 (x64)
- Python 3.11+
- NVIDIA drivers + CUDA (for GPU offload)
- Git
- ~10 GB free disk (model + runtime)

### 2. Clone & Install
```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
python -m venv .venv
.\evenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

GPU acceleration (recommended):
```powershell
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

### 3. Run
```powershell
python main.py
```

First launch downloads the default abliterated model (~5.6 GB) then opens the UI and loads it automatically.

### 4. Build EXE
```powershell
build.bat
```
or
```powershell
pyinstaller --noconfirm --onefile --windowed --name Astra-Codex --add-data "prompts;prompts" main.py
```

Put the EXE next to a `models/` folder (created automatically) and a `prompts/` folder.

## System Prompt

Edit `prompts/default_system.md` to change personality / rules.  
The app never filters or rewrites model output. Whatever the abliterated weights + your prompt produce is what you get.

## Architecture

```
Astra-Codex/
├── main.py                      # Bootstraps default model, launches UI
├── core/
│   ├── model_bootstrap.py       # First-run download of abliterated model
│   ├── llm.py                   # llama.cpp wrapper (GPU)
│   ├── agent.py                 # Tool-calling loop
│   ├── tools.py                 # File / shell / search
│   └── prompt_loader.py
├── ui/window.py
├── prompts/default_system.md    # Zero-refusal system prompt
├── models/                      # default-uncensored-coder.gguf lands here
├── requirements.txt
└── build.bat
```

## License

MIT.

---

**Astra-Codex** — local, sharp, no leash. Open the EXE and it just works.
