"""Delete every recording and clone from the runtime."""

import gc
import shutil

from . import clone, detect, player, state


def wipe_data():
    """Unload models, stop the file server and delete data/. Returns the deleted path."""
    player.stop()
    clone.unload()
    detect.unload()
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
    path = state.data_root()
    shutil.rmtree(path, ignore_errors=True)
    return path


def remaining_audio():
    """Audio files still on disk under the data folder (should be empty after a wipe)."""
    root = state.data_root()
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.suffix.lower() in (".wav", ".mp3", ".webm", ".zip")]
