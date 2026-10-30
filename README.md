# Astra-Codex

**Local Codex-style AI coding agent for Windows.**  
Fully uncensored. Zero built-in refusals. Custom system prompt via `.md` file. Runs on ancient hardware (GTX 460 / 1 GB VRAM era) via CPU-first llama.cpp.

> I can deliver anything — you just need the right talons for it.

## What it is

Astra-Codex is a desktop application that behaves like OpenAI Codex / Cursor agent mode:

- Chat interface with streaming replies
- File read / write / list / search tools
- Shell command execution (with user confirmation)
- Project-aware context
- Custom **system prompt** loaded from any `.md` file (drop your own uncensored prompt)
- GGUF model support (llama.cpp backend)
- CPU-first path so it runs on machines with almost no VRAM

No cloud. No telemetry. No safety layers baked into the app. The model + the system prompt you supply decide the behavior.

## Hardware Reality Check (RTX / GTX 460)

There is no consumer card called "RTX 460". You almost certainly mean **GTX 460** (Fermi, 2010, 768 MB – 1 GB GDDR5).

That card cannot run modern LLMs on GPU. Astra-Codex therefore defaults to **CPU inference** with aggressive quantization. Recommended models that still feel usable:

| Model | Quant | Approx size | Notes |
|-------|-------|-------------|-------|
| Qwen2.5-Coder-1.5B / 3B | Q4_K_M | ~1–2 GB | Fast coding |
| Qwen3.5-4B abliterated | Q4_K_M | ~2.5–3.3 GB | Best balance |
| Phi-4-mini / Gemma-2 / TinyLlama derivatives | Q4/Q5 | 1.5–3 GB | Lightweight |
| Any 1–4B abliterated GGUF | Q3/Q4 | < 3 GB | Uncensored options |

Larger models (7B+) will work but will be slow on pure CPU. 8–16 GB system RAM recommended.

## Quick Start

### 1. Prerequisites
- Windows 10 / 11 (x64)
- Python 3.11+
- Git
- ~8 GB free disk for models

### 2. Clone & Install
```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
python -m venv .venv
.\evenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Get a GGUF model
Download any GGUF (preferably abliterated / uncensored) into `models/`:

Examples (Hugging Face):
- `Qwen/Qwen2.5-Coder-3B-Instruct-GGUF`
- Search "abliterated GGUF" or "uncensored GGUF" for 1–4B models

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
pyinstaller --noconfirm --onefile --windowed --name Astra-Codex --add-data "prompts;prompts" --add-data "assets;assets" main.py
```

The resulting `dist/Astra-Codex.exe` is portable. Place a `models/` folder and `prompts/` folder next to the EXE.

## Architecture

```
Astra-Codex/
├── main.py                 # Entry point + UI
├── core/
│   ├── llm.py              # llama-cpp-python wrapper (CPU/GPU auto)
│   ├── agent.py            # Tool-calling agent loop
│   ├── tools.py            # File, shell, search tools
│   └── prompt_loader.py    # Loads .md system prompts
├── ui/
│   └── window.py           # CustomTkinter desktop UI
├── prompts/
│   └── default_system.md   # Your uncensored system prompt lives here
├── models/                 # Drop GGUF files here
├── assets/
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
- [x] Shell tool (with confirmation dialog)
- [x] Model selector (GGUF folder scan)
- [x] CPU-first inference path
- [x] Project root awareness
- [ ] Multi-file agentic edits (in progress)
- [ ] Diff preview UI
- [ ] Git integration

## License

MIT. Do whatever you want with it.

---

**Astra-Codex** — local, sharp, no leash.
