"""Bootstrap the built-in uncensored models on first run."""

from pathlib import Path
import urllib.request
import sys
from typing import List, Dict

# Two fully abliterated models for RTX 4060 8GB
# Both have refusal direction removed.
MODELS: List[Dict] = [
    {
        "id": "qwen35-9b",
        "display": "Qwen3.5-9B Abliterated (fast)",
        "local_name": "qwen35-9b-abliterated.gguf",
        "repo": "mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF",
        "file": "Huihui-Qwen3.5-9B-abliterated.Q4_K_M.gguf",
        "size_gb": 5.6,
        "note": "Best daily driver — fast + strong reasoning",
    },
    {
        "id": "coder-14b",
        "display": "Qwen2.5-Coder-14B Abliterated (stronger code)",
        "local_name": "qwen25-coder-14b-abliterated.gguf",
        "repo": "bartowski/Qwen2.5-Coder-14B-Instruct-abliterated-GGUF",
        "file": "Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_M.gguf",
        "size_gb": 8.5,
        "note": "Stronger pure coding — fewer errors, slower",
    },
]

DEFAULT_MODEL_ID = "qwen35-9b"


def _url(repo: str, file: str) -> str:
    return f"https://huggingface.co/{repo}/resolve/main/{file}"


def ensure_model(model: Dict, models_dir: Path) -> Path:
    """Download one model if missing. Returns local path."""
    target = models_dir / model["local_name"]
    if target.exists() and target.stat().st_size > 1_000_000_000:
        return target

    # Accept original filename too
    alt = models_dir / model["file"]
    if alt.exists() and alt.stat().st_size > 1_000_000_000:
        return alt

    url = _url(model["repo"], model["file"])
    print(f"[Astra-Codex] Downloading {model['display']}")
    print(f"  {model['file']} (~{model['size_gb']} GB)")
    print(f"  {url}")
    print("  Leave this window open.")

    tmp = target.with_suffix(".gguf.partial")

    def _progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100.0, downloaded * 100.0 / total_size)
            mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  {pct:5.1f}%  ({mb:.0f} / {total_mb:.0f} MB)")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, tmp, reporthook=_progress)
        print()
        tmp.rename(target)
        print(f"[Astra-Codex] Ready: {target.name}")
        return target
    except Exception as e:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download {model['display']}.\n"
            f"Manual: {url}\n"
            f"Place as {model['local_name']} in models/\nError: {e}"
        ) from e


def ensure_default_models(models_dir: str | Path = "models") -> List[Path]:
    """Ensure both built-in models exist. Returns list of local paths."""
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for m in MODELS:
        try:
            paths.append(ensure_model(m, models_dir))
        except Exception as e:
            print(f"[Astra-Codex] Warning: could not get {m['display']}: {e}")
    return paths


def list_builtin_models() -> List[Dict]:
    return MODELS


def get_model_by_id(model_id: str) -> Dict | None:
    for m in MODELS:
        if m["id"] == model_id:
            return m
    return None
