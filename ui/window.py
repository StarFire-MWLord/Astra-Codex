from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.llm import LocalLLM, find_gguf_models
from core.agent import Agent
from core.tools import ToolBelt
from core.prompt_loader import PromptLoader


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

        self._build_ui()
        self._refresh_models()
        self._refresh_prompts()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(self, width=260, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)

        ctk.CTkLabel(side, text="Astra-Codex", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(16, 4), padx=12, anchor="w"
        )
        ctk.CTkLabel(side, text="local · uncensored · sharp", text_color="gray").pack(
            padx=12, anchor="w"
        )

        ctk.CTkLabel(side, text="Model").pack(pady=(18, 2), padx=12, anchor="w")
        self.model_var = ctk.StringVar(value="(no models)")
        self.model_menu = ctk.CTkOptionMenu(side, variable=self.model_var, values=["(no models)"])
        self.model_menu.pack(fill="x", padx=12)

        ctk.CTkButton(side, text="Load Model", command=self._load_model).pack(
            fill="x", padx=12, pady=(8, 0)
        )

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

        ctk.CTkLabel(side, text="Project Root").pack(pady=(18, 2), padx=12, anchor="w")
        self.root_label = ctk.CTkLabel(side, text=str(self.project_root), wraplength=230, anchor="w")
        self.root_label.pack(fill="x", padx=12)
        ctk.CTkButton(side, text="Choose Folder", command=self._choose_root).pack(
            fill="x", padx=12, pady=(6, 0)
        )

        self.status = ctk.CTkLabel(side, text="No model loaded", text_color="orange")
        self.status.pack(side="bottom", pady=16, padx=12, anchor="w")

        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.chat = ctk.CTkTextbox(main, wrap="word", font=ctk.CTkFont(size=13))
        self.chat.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.chat.insert("end", "Astra-Codex online.\nDrop a GGUF into models/, load it, then talk.\n\n")
        self.chat.configure(state="disabled")

        bottom = ctk.CTkFrame(main)
        bottom.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        bottom.grid_columnconfigure(0, weight=1)

        self.input = ctk.CTkTextbox(bottom, height=80)
        self.input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input.bind("<Control-Return>", lambda e: self._send())

        ctk.CTkButton(bottom, text="Send", width=100, command=self._send).grid(row=0, column=1)

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

    def _load_model(self):
        name = self.model_var.get()
        if name == "(no models)":
            messagebox.showinfo("No models", "Put a .gguf file in the models/ folder.")
            return
        path = self.models_dir / name
        self.status.configure(text="Loading…", text_color="yellow")
        self.update_idletasks()

        def work():
            try:
                # -1 = offload all layers to GPU (RTX 4060 8GB)
                self.llm = LocalLLM(path, n_ctx=8192, n_gpu_layers=-1)
                sys_prompt = self.prompt_loader.load(self.prompt_var.get())
                tools = ToolBelt(self.project_root)
                self.agent = Agent(self.llm, tools, sys_prompt)
                self.after(0, lambda: self.status.configure(
                    text=f"Loaded: {name} (GPU)", text_color="lightgreen"
                ))
                self.after(0, lambda: self._append("system", f"Model loaded: {name} (GPU offload)"))
            except Exception as e:
                self.after(0, lambda: self.status.configure(text=f"Error: {e}", text_color="red"))
                self.after(0, lambda: messagebox.showerror("Load failed", str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _on_prompt_change(self, *_):
        if not self.agent:
            return
        sys_prompt = self.prompt_loader.load(self.prompt_var.get())
        self.agent.reset(sys_prompt)
        self._append("system", f"System prompt switched to: {self.prompt_var.get()}")

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
            messagebox.showinfo("No model", "Load a GGUF model first.")
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
