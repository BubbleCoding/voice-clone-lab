import base64
import warnings

import numpy as np

from conftest import speechlike
from lab import audio, colab_io, player, state


def _clip():
    return audio.save(state.subdir("real") / "NL1_echt.wav", speechlike(2))


def test_colab_player_holds_no_audio(monkeypatch):
    path = _clip()
    registered = {}
    monkeypatch.setattr(colab_io, "in_colab", lambda: True)
    monkeypatch.setattr(colab_io, "register_callback", lambda name, func: registered.update({name: func}))
    tag = player.cell(path)
    assert registered == {player.CALLBACK: player.serve_clip}
    assert '"real/NL1_echt.wav"' in tag
    assert "data:audio" not in tag and len(tag) < 2000


def test_serve_clip_returns_the_file():
    path = _clip()
    result = player.serve_clip("real/NL1_echt.wav")
    assert base64.b64decode(result.data["data"]) == path.read_bytes()


def test_serve_clip_stays_inside_data_folder():
    _clip()
    (state.data_root().parent / "secret.wav").write_bytes(b"x")
    assert player.serve_clip("../secret.wav").data == {"error": "not found"}
    assert player.serve_clip("real/missing.wav").data == {"error": "not found"}


def test_loud_peaks_are_limited_without_warning():
    wav = np.zeros(audio.SR * 2, dtype=np.float32)
    wav[::2400] = 1.0  # quiet signal with sharp clicks: normalizing pushes the clicks past 0 dBFS
    wav += speechlike(2) * 0.01
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = audio.normalize_loudness(wav)
    assert np.max(np.abs(out)) <= 10 ** (-1 / 20) + 1e-6
