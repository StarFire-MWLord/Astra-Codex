#!/usr/bin/env python3
"""Astra-Codex — local uncensored Codex-style coding agent."""

from core.model_bootstrap import ensure_default_models
from ui.window import AstraWindow


def main():
    # First launch pulls both abliterated models so the switcher is ready.
    try:
        ensure_default_models("models")
    except Exception as e:
        print(f"[Astra-Codex] Model bootstrap warning: {e}")
        print("You can still drop any GGUF into models/ manually.")

    app = AstraWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
