from __future__ import annotations

import json
import re
from typing import Callable, Generator, Optional

from .llm import LocalLLM
from .tools import ToolBelt, TOOL_SCHEMAS
from .prompt_loader import PromptLoader


TOOL_INSTRUCTION = """
You have these tools. When you need one, emit EXACTLY this XML block and nothing else in that message:

<tool_call>
{"name": "tool_name", "arguments": {"arg": "value"}}
</tool_call>

Available tools:
""" + "\n".join(
    f"- {t['name']}: {t['description']} | params: {t['parameters']}" for t in TOOL_SCHEMAS
) + """

After the tool result is returned to you, continue the task. Do not invent tool results.
"""


def classify_risk(tool_name: str, args: dict) -> str:
    """high = shell / delete / large overwrite; medium = any write; low = read/search"""
    name = (tool_name or "").lower()
    if name in ("run_shell", "shell", "execute", "delete", "rm"):
        return "high"
    if name in ("write_file", "edit_file", "apply_patch"):
        content = str(args.get("content", ""))
        if len(content) > 2000:
            return "high"
        return "medium"
    if name in ("mkdir", "create_dir"):
        return "medium"
    return "low"


def needs_approval(access_level: str, risk: str) -> bool:
    level = (access_level or "medium").lower()
    if level == "full":
        return False
    if level == "medium":
        return risk == "high"
    # low
    return risk in ("medium", "high")


class Agent:
    def __init__(
        self,
        llm: LocalLLM,
        tools: ToolBelt,
        system_prompt: str,
        max_tool_rounds: int = 8,
        access_level: str = "medium",
        approval_callback: Optional[Callable[[str, dict, str], bool]] = None,
    ):
        self.llm = llm
        self.tools = tools
        self.system = system_prompt.strip() + "\n\n" + TOOL_INSTRUCTION
        self.max_tool_rounds = max_tool_rounds
        self.access_level = access_level
        self.approval_callback = approval_callback
        self.history: list[dict] = [{"role": "system", "content": self.system}]

    def set_access(self, level: str):
        self.access_level = level

    def reset(self, system_prompt: Optional[str] = None):
        if system_prompt:
            self.system = system_prompt.strip() + "\n\n" + TOOL_INSTRUCTION
        self.history = [{"role": "system", "content": self.system}]

    def _extract_tool(self, text: str) -> Optional[dict]:
        m = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", text, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            return None

    def _run_tool(self, call: dict) -> str:
        name = call.get("name", "")
        args = call.get("arguments") or {}
        risk = classify_risk(name, args)

        if needs_approval(self.access_level, risk):
            if self.approval_callback:
                approved = self.approval_callback(name, args, risk)
                if not approved:
                    return f"Denied by user (access={self.access_level}, risk={risk})"
            else:
                return f"Approval required but no callback (access={self.access_level}, risk={risk})"

        fn = getattr(self.tools, name, None)
        if not callable(fn):
            return f"Unknown tool: {name}"
        try:
            return str(fn(**args))
        except TypeError as e:
            return f"Bad arguments for {name}: {e}"
        except Exception as e:
            return f"Tool error ({name}): {e}"

    def run(
        self,
        user_message: str,
        stream: bool = True,
        on_tool: Optional[Callable[[str, str], None]] = None,
    ) -> Generator[str, None, None] | str:
        self.history.append({"role": "user", "content": user_message})

        for _ in range(self.max_tool_rounds + 1):
            if stream:
                full = []
                for token in self.llm.chat(self.history, stream=True):
                    full.append(token)
                    yield token
                reply = "".join(full)
            else:
                reply = self.llm.chat(self.history, stream=False)

            self.history.append({"role": "assistant", "content": reply})

            call = self._extract_tool(reply)
            if not call:
                break

            result = self._run_tool(call)
            if on_tool:
                on_tool(call.get("name", "?"), result)

            tool_msg = f"Tool `{call.get('name')}` result:\n```\n{result}\n```"
            self.history.append({"role": "user", "content": tool_msg})

            if stream:
                yield f"\n\n[tool: {call.get('name')}]\n"

        if not stream:
            return reply
