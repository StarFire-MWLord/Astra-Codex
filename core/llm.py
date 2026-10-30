from pathlib import Path
from typing import Generator, Optional
import os


class LocalLLM:
    """Thin wrapper around llama-cpp-python. GPU offload for RTX 4060-class cards."""

    def __init__(
        self,
        model_path: str | Path,
        n_ctx: int = 8192,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = -1,  # -1 = offload all layers to GPU (RTX 4060)
        verbose: bool = False,
    ):
        from llama_cpp import Llama

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        threads = n_threads or max(1, (os.cpu_count() or 4) - 1)

        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=threads,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose,
            chat_format="chatml",
        )
        self.n_gpu_layers = n_gpu_layers

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ):
        if stream:
            return self._stream(messages, temperature, max_tokens)
        out = self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        return out["choices"][0]["message"]["content"]

    def _stream(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> Generator[str, None, None]:
        stream = self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta and delta["content"]:
                yield delta["content"]


def find_gguf_models(models_dir: str | Path = "models") -> list[Path]:
    d = Path(models_dir)
    if not d.exists():
        return []
    return sorted(d.glob("**/*.gguf"))
