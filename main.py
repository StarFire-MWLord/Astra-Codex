#!/usr/bin/env python3
"""Astra-Codex — local uncensored Codex-style coding agent."""

from core.model_bootstrap import ensure_default_model
from ui.window import AstraWindow


def main():
    # First launch: pull the built-in abliterated Qwen2.5-Coder-7B (~4.7 GB)
    # so the EXE opens ready to work with zero refusal rate.
    try:
        ensure_default_model("models")
    except Exception as e:
        print(f"[Astra-Codex] Model bootstrap warning: {e}")
        print("You can still drop any GGUF into models/ manually.")

    app = AstraWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
