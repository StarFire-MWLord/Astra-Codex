# Astra-Codex

**Local Codex-style AI coding agent for Windows.**  
Fully uncensored. Zero built-in refusals. Dual abliterated models with mid-chat switching. Tuned for **RTX 4060 (8 GB)**.

> I can deliver anything — you just need the right talons for it.

## One-Click Install (Recommended)

1. Install **Python 3.11+** from python.org (check “Add to PATH”)
2. Install **Git** if you don’t have it
3. Open PowerShell and run:

```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
INSTALL.bat
```

The installer will:
- Reuse existing Python packages when possible (no double install)
- Create / reuse a virtual environment
- Install CUDA llama-cpp-python for your 4060
- Download both abliterated models (skips if already present)
- Build `Astra-Codex.exe`
- Create a **Desktop shortcut**

When it finishes, just double-click **Astra-Codex** on your desktop.

## Built-in models (switch anytime)

| Model | Size | Role |
|-------|------|------|
| **Qwen3.5-9B Abliterated** | ~5.6 GB | Fast daily driver |
| **Qwen2.5-Coder-14B Abliterated** | ~8.5 GB | Stronger code, fewer errors |

Both fully abliterated. Switch mid-conversation — chat memory is kept.

## Manual install (if you prefer)

```powershell
git clone https://github.com/StarFire-MWLord/Astra-Codex.git
cd Astra-Codex
python -m venv .venv
.\evenv\Scripts\Activate.ps1
pip install -r requirements.txt
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
python main.py
```

## License

MIT.

---

**Astra-Codex** — local, sharp, no leash.
