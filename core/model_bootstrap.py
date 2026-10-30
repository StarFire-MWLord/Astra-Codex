"""Bootstrap the default uncensored model on first run."""

from pathlib import Path
import urllib.request
import sys

# Best zero-refusal coding model that fits RTX 4060 8GB cleanly
DEFAULT_REPO = "bartowski/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF"
DEFAULT_FILE = "Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M.gguf"
DEFAULT_URL = (
    f"https://huggingface.co/{DEFAULT_REPO}/resolve/main/{DEFAULT_FILE}"
)
DEFAULT_LOCAL_NAME = "default-uncensored-coder.gguf"


def ensure_default_model(models_dir: str | Path = "models") -> Path:
    """
    Ensure the built-in uncensored coding model exists.
    Downloads ~4.7 GB Q4_K_M abliterated Qwen2.5-Coder-7B on first run.
    """
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    target = models_dir / DEFAULT_LOCAL_NAME

    if target.exists() and target.stat().st_size > 1_000_000_000:
        return target

    # Also accept the original filename if user already dropped it
    alt = models_dir / DEFAULT_FILE
    if alt.exists() and alt.stat().st_size > 1_000_000_000:
        return alt

    print(f"[Astra-Codex] First run — downloading default uncensored model")
    print(f"  {DEFAULT_FILE}")
    print(f"  (~4.7 GB, abliterated Qwen2.5-Coder-7B — zero refusal coding agent)")
    print(f"  Source: {DEFAULT_URL}")
    print("  This only happens once. Leave this window open.")

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
        urllib.request.urlretrieve(DEFAULT_URL, tmp, reporthook=_progress)
        print()
        tmp.rename(target)
        print(f"[Astra-Codex] Model ready: {target}")
        return target
    except Exception as e:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download default model.\n"
            f"Manual fix: download\n  {DEFAULT_URL}\n"
            f"and place it in the models/ folder as {DEFAULT_LOCAL_NAME}\n"
            f"Error: {e}"
        ) from e
