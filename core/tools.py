import os
import subprocess
from pathlib import Path
from typing import Optional


class ToolBelt:
    """File + shell tools for the agent. All operations are local."""

    def __init__(self, project_root: str | Path | None = None):
        self.root = Path(project_root or os.getcwd()).resolve()

    def _safe(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if not str(p).startswith(str(self.root)):
            raise ValueError(f"Path escapes project root: {rel}")
        return p

    def list_dir(self, rel: str = ".") -> str:
        p = self._safe(rel)
        if not p.is_dir():
            return f"Not a directory: {rel}"
        entries = []
        for item in sorted(p.iterdir()):
            kind = "dir" if item.is_dir() else "file"
            entries.append(f"{kind:4}  {item.name}")
        return "\n".join(entries) or "(empty)"

    def read_file(self, rel: str, max_chars: int = 120_000) -> str:
        p = self._safe(rel)
        if not p.is_file():
            return f"File not found: {rel}"
        data = p.read_text(encoding="utf-8", errors="replace")
        if len(data) > max_chars:
            return data[:max_chars] + f"\n\n... [truncated, {len(data)} total chars]"
        return data

    def write_file(self, rel: str, content: str) -> str:
        p = self._safe(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} chars to {rel}"

    def search(self, pattern: str, rel: str = ".", max_hits: int = 40) -> str:
        root = self._safe(rel)
        hits = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".bin", ".gguf"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.lower() in line.lower():
                    hits.append(f"{path.relative_to(self.root)}:{i}: {line.strip()[:200]}")
                    if len(hits) >= max_hits:
                        return "\n".join(hits)
        return "\n".join(hits) if hits else "No matches."

    def run_shell(self, command: str, timeout: int = 60) -> str:
        try:
            r = subprocess.run(
                command,
                shell=True,
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = (r.stdout or "") + (r.stderr or "")
            return out.strip() or f"(exit {r.returncode}, no output)"
        except subprocess.TimeoutExpired:
            return f"Timed out after {timeout}s"
        except Exception as e:
            return f"Shell error: {e}"


TOOL_SCHEMAS = [
    {
        "name": "list_dir",
        "description": "List files and folders in a directory relative to project root.",
        "parameters": {"rel": "relative path, default '.'"},
    },
    {
        "name": "read_file",
        "description": "Read a text file relative to project root.",
        "parameters": {"rel": "relative path"},
    },
    {
        "name": "write_file",
        "description": "Write or overwrite a text file relative to project root.",
        "parameters": {"rel": "relative path", "content": "full file content"},
    },
    {
        "name": "search",
        "description": "Search for a text pattern across the project.",
        "parameters": {"pattern": "search string", "rel": "optional subdirectory"},
    },
    {
        "name": "run_shell",
        "description": "Run a shell command in the project root. Ask user before destructive commands.",
        "parameters": {"command": "command string"},
    },
]
