import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lab import audio, clone, detect, player, state  # noqa: E402


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("VCL_DATA_DIR", str(tmp_path / "data"))
    yield tmp_path / "data"
    player.stop()
    clone.unload()
    detect.unload()


def speechlike(seconds, sr=audio.SR, seed=0):
    """Bursts of harmonic tone separated by short silences, roughly like read speech."""
    rng = np.random.default_rng(seed)
    out = []
    while sum(len(x) for x in out) < seconds * sr:
        n = int(rng.uniform(0.3, 0.9) * sr)
        t = np.arange(n) / sr
        f0 = rng.uniform(100, 220)
        burst = sum(np.sin(2 * np.pi * f0 * k * t) / k for k in range(1, 5)) * np.hanning(n) * 0.3
        out += [burst.astype(np.float32), np.zeros(int(0.25 * sr), dtype=np.float32)]
    return np.concatenate(out)[: int(seconds * sr)]


@pytest.fixture
def consented():
    state.record_consent("K7QM", "A", [True] * 4)


@pytest.fixture
def recordings(consented):
    ref = audio.save(state.subdir("real") / "leestekst.wav", speechlike(22, seed=1))
    state.register_recording("reference", ref)
    target = audio.save(state.subdir("real") / "NL1_echt.wav", speechlike(5, seed=2))
    state.register_recording("target", target)
    return ref, target


class _Tensor:
    def __init__(self, arr):
        self.arr = arr

    def squeeze(self, _dim):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.arr


class FakeModel:
    """Stands in for ChatterboxMultilingualTTS: a tone whose length follows the text."""
    sr = audio.SR

    def __init__(self):
        self.conditioned = []

    def prepare_conditionals(self, path, exaggeration=0.5):
        self.conditioned.append(path)

    def generate(self, text, language_id, **settings):
        self.settings = settings
        n = int(self.sr * (0.06 * len(text) + 0.5))
        return _Tensor((0.2 * np.sin(2 * np.pi * 180 * np.arange(n) / self.sr)).astype(np.float32))


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(clone, "MODEL", model)
    monkeypatch.setattr(clone, "MODEL_VERSION", "fake")
    return model


NOTEBOOK = Path(__file__).resolve().parent.parent / "voice_clone_lab.ipynb"


def notebook_cell(marker):
    """Source of the notebook code cell that contains marker."""
    cells = json.loads(NOTEBOOK.read_text())["cells"]
    matches = ["".join(c["source"]) for c in cells if c["cell_type"] == "code" and marker in "".join(c["source"])]
    assert len(matches) == 1, marker
    return matches[0]


def run_cell(marker, replace=None):
    """Execute a notebook code cell with the names the setup cell imports."""
    import time
    import pandas as pd
    from IPython.display import display
    from lab import audio, clone, detect, player, state, texts
    from lab import cells as ui
    source = notebook_cell(marker)
    for old, new in (replace or {}).items():
        assert old in source, old
        source = source.replace(old, new)
    namespace = {"time": time, "pd": pd, "display": display, "audio": audio, "clone": clone, "detect": detect,
                 "player": player, "state": state, "texts": texts, "ui": ui}
    exec(compile(source, f"<notebook: {marker}>", "exec"), namespace)
    return namespace


def run_experiment():
    return run_cell("REF_LENGTHS = [3, 6, 10]")["results"]
