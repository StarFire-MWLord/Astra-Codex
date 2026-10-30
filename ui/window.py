from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional, Dict, List

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.llm import LocalLLM, find_gguf_models
from core.agent import Agent
from core.tools import ToolBelt
from core.prompt_loader import PromptLoader
from core.model_bootstrap import (
    MODELS,
    DEFAULT_MODEL_ID,
    list_builtin_models,
    get_model_by_id,
    ensure_default_models,
)


class AstraWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Astra-Codex")
        self.geometry("1100x720")
        self.minsize(800, 500)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.llm: Optional[LocalLLM] = None
        self.agent: Optional[Agent] = None
        self.prompt_loader = PromptLoader("prompts")
        self.project_root = Path.cwd()
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

        # Shared conversation history survives model switches
        self.shared_history: List[dict] = []

        self._build_ui()
        self._refresh_models()
        self._refresh_prompts()

        # Prefer built-in fast model and auto-load
        self.after(400, self._auto_load_default)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(self, width=280, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)

        ctk.CTkLabel(side, text="Astra-Codex", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(16, 4), padx=12, anchor="w"
        )
        ctk.CTkLabel(side, text="local · uncensored · dual model", text_color="gray").pack(
            padx=12, anchor="w"
        )

        # --- Built-in model switcher (Codex-style) ---
        ctk.CTkLabel(side, text="Built-in Models (switch anytime)").pack(
            pady=(18, 2), padx=12, anchor="w"
        )

        self.builtin_var = ctk.StringVar(value=DEFAULT_MODEL_ID)
        for m in MODELS:
            rb = ctk.CTkRadioButton(
                side,
                text=m["display"],
                variable=self.builtin_var,
                value=m["id"],
                command=self._on_builtin_switch,
            )
            rb.pack(anchor="w", padx=16, pady=2)

        ctk.CTkLabel(
            side,
            text="Switch mid-chat keeps full memory",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).pack(padx=12, pady=(2, 8), anchor="w")

        # --- Access level ---
        ctk.CTkLabel(side, text="Access Level").pack(pady=(12, 2), padx=12, anchor="w")
        self.access_var = ctk.StringVar(value="medium")
        for label, val in [
            ("Full (auto everything)", "full"),
            ("Medium (approve high-risk)", "medium"),
            ("Low (approve medium+high)", "low"),
        ]:
            ctk.CTkRadioButton(
                side,
                text=label,
                variable=self.access_var,
                value=val,
                command=self._on_access_change,
            ).pack(anchor="w", padx=16, pady=1)

        # --- Any GGUF fallback ---
        ctk.CTkLabel(side, text="Or any GGUF in models/").pack(pady=(8, 2), padx=12, anchor="w")
        self.model_var = ctk.StringVar(value="(no models)")
        self.model_menu = ctk.CTkOptionMenu(side, variable=self.model_var, values=["(no models)"])
        self.model_menu.pack(fill="x", padx=12)

        ctk.CTkButton(side, text="Load Selected GGUF", command=self._load_gguf).pack(
            fill="x", padx=12, pady=(8, 0)
        )

        # --- System prompt ---
        ctk.CTkLabel(side, text="System Prompt (.md)").pack(pady=(18, 2), padx=12, anchor="w")
        self.prompt_var = ctk.StringVar(value="default_system")
        self.prompt_menu = ctk.CTkOptionMenu(
            side, variable=self.prompt_var, values=["default_system"], command=self._on_prompt_change
        )
        self.prompt_menu.pack(fill="x", padx=12)

        ctk.CTkButton(side, text="Reload Prompt", command=self._on_prompt_change).pack(
            fill="x", padx=12, pady=(8, 0)
        )
        ctk.CTkButton(side, text="Open Prompts Folder", command=self._open_prompts).pack(
            fill="x", padx=12, pady=(6, 0)
        )

        # --- Project root ---
        ctk.CTkLabel(side, text="Project Root").pack(pady=(18, 2), padx=12, anchor="w")
        self.root_label = ctk.CTkLabel(side, text=str(self.project_root), wraplength=250, anchor="w")
        self.root_label.pack(fill="x", padx=12)
        ctk.CTkButton(side, text="Choose Folder", command=self._choose_root).pack(
            fill="x", padx=12, pady=(6, 0)
        )

        self.status = ctk.CTkLabel(side, text="No model loaded", text_color="orange")
        self.status.pack(side="bottom", pady=16, padx=12, anchor="w")

        # --- Chat area ---
        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.chat = ctk.CTkTextbox(main, wrap="word", font=ctk.CTkFont(size=13))
        self.chat.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.chat.insert(
            "end",
            "Astra-Codex online.\n"
            "Two built-in abliterated models — switch anytime, memory stays.\n"
            "• Qwen3.5-9B  → fast daily driver\n"
            "• Qwen2.5-Coder-14B → stronger code, fewer errors\n\n",
        )
        self.chat.configure(state="disabled")

        bottom = ctk.CTkFrame(main)
        bottom.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        bottom.grid_columnconfigure(0, weight=1)

        self.input = ctk.CTkTextbox(bottom, height=80)
        self.input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input.bind("<Control-Return>", lambda e: self._send())

        ctk.CTkButton(bottom, text="Send", width=100, command=self._send).grid(row=0, column=1)

    def _on_access_change(self):
        if self.agent:
            self.agent.set_access(self.access_var.get())

    def _request_approval(self, tool_name: str, args: dict, risk: str) -> bool:
        """Blocking modal on main thread via after + wait."""
        result = [False]
        event = threading.Event()

        def show():
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Approve {risk.upper()} action?")
            dialog.geometry("520x280")
            dialog.attributes("-topmost", True)
            ctk.CTkLabel(
                dialog,
                text=f"Tool: {tool_name}\nRisk: {risk}\nAccess: {self.access_var.get()}\n\nArgs:\n{str(args)[:400]}",
                justify="left",
                wraplength=480,
            ).pack(pady=16, padx=16)

            def yes():
                result[0] = True
                dialog.destroy()
                event.set()

            def no():
                result[0] = False
                dialog.destroy()
                event.set()

            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="Approve", command=yes, fg_color="green").pack(side="left", padx=12)
            ctk.CTkButton(btn_frame, text="Deny", command=no, fg_color="red").pack(side="left", padx=12)
            dialog.protocol("WM_DELETE_WINDOW", no)

        self.after(0, show)
        event.wait(timeout=300)
        return result[0]

    # ------------------------------------------------------------------
    # Model loading / switching
    # ------------------------------------------------------------------

    def _auto_load_default(self):
        """First launch: ensure models exist, then load the fast 9B."""
        self.status.configure(text="Checking models…", text_color="yellow")

        def work():
            try:
                ensure_default_models(self.models_dir)
                self.after(0, self._refresh_models)
                self.after(0, lambda: self._load_builtin(DEFAULT_MODEL_ID))
            except Exception as e:
                self.after(0, lambda: self.status.configure(
                    text=f"Bootstrap: {e}", text_color="orange"
                ))

        threading.Thread(target=work, daemon=True).start()

    def _on_builtin_switch(self):
        mid = self.builtin_var.get()
        self._load_builtin(mid)

    def _load_builtin(self, model_id: str):
        info = get_model_by_id(model_id)
        if not info:
            return

        path = self.models_dir / info["local_name"]
        if not path.exists():
            # try original filename
            path = self.models_dir / info["file"]
        if not path.exists():
            self.status.configure(text="Model file missing — downloading…", text_color="yellow")
            def dl():
                try:
                    from core.model_bootstrap import ensure_model
                    ensure_model(info, self.models_dir)
                    self.after(0, lambda: self._load_builtin(model_id))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Download failed", str(e)))
            threading.Thread(target=dl, daemon=True).start()
            return

        self._swap_model(path, info["display"])

    def _load_gguf(self):
        name = self.model_var.get()
        if name == "(no models)":
            messagebox.showinfo("No models", "Put a .gguf file in the models/ folder.")
            return
        path = self.models_dir / name
        self._swap_model(path, name)

    def _swap_model(self, path: Path, display_name: str):
        """Load new model while preserving conversation history."""
        self.status.configure(text=f"Loading {display_name}…", text_color="yellow")
        self.update_idletasks()

        # Snapshot current history (skip system message)
        old_history = []
        if self.agent and len(self.agent.history) > 1:
            old_history = [m for m in self.agent.history if m["role"] != "system"]

        def work():
            try:
                # 14B may need fewer GPU layers on 8GB; 9B can take all
                n_gpu = -1
                if "14B" in display_name or "14b" in display_name.lower():
                    n_gpu = 28  # leave a little headroom

                llm = LocalLLM(path, n_ctx=8192, n_gpu_layers=n_gpu)
                sys_prompt = self.prompt_loader.load(self.prompt_var.get())
                tools = ToolBelt(self.project_root)
                agent = Agent(
                    llm,
                    tools,
                    sys_prompt,
                    access_level=self.access_var.get(),
                    approval_callback=self._request_approval,
                )

                # Restore conversation memory
                if old_history:
                    agent.history.extend(old_history)

                self.llm = llm
                self.agent = agent

                self.after(0, lambda: self.status.configure(
                    text=f"Loaded: {display_name}", text_color="lightgreen"
                ))
                self.after(0, lambda: self._append(
                    "system",
                    f"Switched to {display_name}\n"
                    f"Conversation memory carried over ({len(old_history)} messages).",
                ))
            except Exception as e:
                self.after(0, lambda: self.status.configure(text=f"Error: {e}", text_color="red"))
                self.after(0, lambda: messagebox.showerror("Load failed", str(e)))

        threading.Thread(target=work, daemon=True).start()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _append(self, role: str, text: str):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"\n[{role}]\n{text}\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _refresh_models(self):
        models = find_gguf_models(self.models_dir)
        names = [m.name for m in models] or ["(no models)"]
        self.model_menu.configure(values=names)
        self.model_var.set(names[0])

    def _refresh_prompts(self):
        names = self.prompt_loader.list_prompts() or ["default_system"]
        self.prompt_menu.configure(values=names)
        if "default_system" in names:
            self.prompt_var.set("default_system")
        else:
            self.prompt_var.set(names[0])

    def _on_prompt_change(self, *_):
        if not self.agent:
            return
        sys_prompt = self.prompt_loader.load(self.prompt_var.get())
        # Keep history, only replace system message
        self.agent.system = sys_prompt.strip() + "\n\n" + self.agent.system.split("You have these tools")[-1] if "You have these tools" in self.agent.system else sys_prompt
        if self.agent.history and self.agent.history[0]["role"] == "system":
            self.agent.history[0] = {"role": "system", "content": self.agent.system}
        self._append("system", f"System prompt → {self.prompt_var.get()}")

    def _open_prompts(self):
        import os
        os.startfile(str(Path("prompts").resolve()))

    def _choose_root(self):
        d = filedialog.askdirectory()
        if d:
            self.project_root = Path(d)
            self.root_label.configure(text=str(self.project_root))
            if self.agent:
                self.agent.tools = ToolBelt(self.project_root)

    def _send(self):
        if not self.agent:
            messagebox.showinfo("No model", "Load a model first.")
            return
        text = self.input.get("1.0", "end").strip()
        if not text:
            return
        self.input.delete("1.0", "end")
        self._append("you", text)

        def work():
            buf = []
            try:
                for token in self.agent.run(text, stream=True):
                    buf.append(token)
                    chunk = "".join(buf)
                    self.after(0, lambda c=chunk: self._set_assistant(c))
            except Exception as e:
                self.after(0, lambda: self._append("error", str(e)))

        self._append("astra", "…")
        threading.Thread(target=work, daemon=True).start()

    def _set_assistant(self, text: str):
        self.chat.configure(state="normal")
        content = self.chat.get("1.0", "end")
        idx = content.rfind("[astra]")
        if idx != -1:
            self.chat.delete("1.0", "end")
            head = content[:idx]
            self.chat.insert("end", head)
            self.chat.insert("end", f"[astra]\n{text}\n")
        else:
            self.chat.insert("end", f"\n[astra]\n{text}\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")
