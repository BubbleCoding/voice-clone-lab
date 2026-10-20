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

    def generate(self, text, language_id):
        n = int(self.sr * (0.06 * len(text) + 0.5))
        return _Tensor((0.2 * np.sin(2 * np.pi * 180 * np.arange(n) / self.sr)).astype(np.float32))


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(clone, "MODEL", model)
    monkeypatch.setattr(clone, "MODEL_VERSION", "fake")
    return model
