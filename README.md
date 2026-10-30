# Astra-Codex

**Local Codex-style AI coding agent for Windows.**  
Fully uncensored. Zero built-in refusals. Custom system prompt via `.md` file. Tuned for **RTX 4060 (8 GB)** and similar cards.

> I can deliver anything — you just need the right talons for it.

## What it is

Astra-Codex is a desktop application that behaves like OpenAI Codex / Cursor agent mode:

- Chat interface with streaming replies
- File read / write / list / search tools
- Shell command execution
- Project-aware context
- Custom **system prompt** loaded from any `.md` file (drop your own uncensored prompt)
- GGUF model support (llama.cpp backend)
- GPU offload for RTX 4060-class cards + CPU fallback

No cloud. No telemetry. No safety layers baked into the app. The model + the system prompt you supply decide the behavior.

## Hardware — RTX 4060 (8 GB)

You have real headroom. Recommended models:

| Model | Quant | Approx size | Notes |
|-------|-------|-------------|-------|
| Qwen2.5-Coder-7B / 14B | Q4_K_M / Q5_K_M | 4–9 GB | Strong coding |
| Qwen3 / Qwen3.5 8–14B abliterated | Q4_K_M | 5–9 GB | Uncensored sweet spot |
| Llama-3.1-8B abliterated | Q4_K_M / Q5_K_M | 4.5–6 GB | Solid all-rounder |
| DeepSeek-Coder / CodeLlama 7B–13B | Q4/Q5 | 4–8 GB | Code-focused |
| Any 7–14B abliterated GGUF | Q4_K_M | fits 8 GB | Zero-refusal options |

Leave a little VRAM free for context (KV cache). 8k–16k context is comfortable on 8 GB with Q4 models.

## Quick Start

### 1. Prerequisites
- Windows 10 / 11 (x64)
- Python 3.11+
- NVIDIA drivers + CUDA (for GPU offload)
- Git
- ~15 GB free disk for models

### 2. Clone & Install
```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
python -m venv .venv
.\evenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For GPU acceleration install the CUDA build of llama-cpp-python (example):
```powershell
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

### 3. Get a GGUF model
Drop any GGUF (preferably abliterated / uncensored) into `models/`.

Good starting points on Hugging Face:
- Qwen2.5-Coder-7B-Instruct GGUF
- Search "abliterated GGUF" or "uncensored GGUF" for 7–14B models

### 4. Drop your system prompt
Edit or replace `prompts/default_system.md` with whatever personality / rules you want. The entire contents of that file become the system message. No filters are applied by the app.

### 5. Run
```powershell
python main.py
```

Or build a standalone EXE (see below).

## Building the EXE

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name Astra-Codex --add-data "prompts;prompts" main.py
```

Or just run `build.bat`.

The resulting `dist/Astra-Codex.exe` is portable. Place a `models/` folder and `prompts/` folder next to the EXE.

## Architecture

```
Astra-Codex/
├── main.py                 # Entry point + UI
├── core/
│   ├── llm.py              # llama-cpp-python wrapper (GPU + CPU)
│   ├── agent.py            # Tool-calling agent loop
│   ├── tools.py            # File, shell, search tools
│   └── prompt_loader.py    # Loads .md system prompts
├── ui/
│   └── window.py           # CustomTkinter desktop UI
├── prompts/
│   └── default_system.md   # Your uncensored system prompt lives here
├── models/                 # Drop GGUF files here
├── requirements.txt
└── build.bat               # One-click EXE build
```

## System Prompt / Uncensored Mode

There is **no** hard-coded refusal logic in Astra-Codex.

Whatever you put in `prompts/*.md` is injected as the system message.  
Want zero refusals? Write a system prompt that says so.  
Want a specific persona, coding style, or jailbreak? Drop the `.md` and select it in the UI.

The app never rewrites, filters, or second-guesses the model output.

## Features (Codex parity targets)

- [x] Streaming chat
- [x] Custom system prompt from .md
- [x] File read / write / list / recursive search
- [x] Shell tool
- [x] Model selector (GGUF folder scan)
- [x] GPU offload (RTX 4060) + CPU fallback
- [x] Project root awareness
- [ ] Multi-file agentic edits (in progress)
- [ ] Diff preview UI
- [ ] Git integration

## License

MIT. Do whatever you want with it.

---

**Astra-Codex** — local, sharp, no leash.
