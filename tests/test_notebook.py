"""Static guardrail checks on the notebook and package source."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = json.loads((ROOT / "voice_clone_lab.ipynb").read_text())
CODE = ["".join(c["source"]) for c in NB["cells"] if c["cell_type"] == "code"]
LAB_SOURCES = {p.name: p.read_text() for p in (ROOT / "lab").glob("*.py")}


def test_notebook_requests_t4_gpu_and_has_no_outputs():
    assert NB["metadata"]["accelerator"] == "GPU"
    assert NB["metadata"]["colab"]["gpuType"] == "T4"
    assert all(c.get("outputs") == [] for c in NB["cells"] if c["cell_type"] == "code")


def test_cell_order_matches_lesson():
    calls = [re.findall(r"lab\.(\w+)\(", src)[-1] for src in CODE]
    assert calls == ["setup", "consent", "record_reference", "record_target", "experiment",
                     "free_mode", "download", "detection", "wipe"]


def test_no_public_links_drive_or_reference_upload():
    everything = "\n".join(CODE + list(LAB_SOURCES.values()))
    for forbidden in ("share=True", "drive.mount", "files.upload", "gradio", "ngrok"):
        assert forbidden not in everything, forbidden


def test_only_colab_io_imports_google_colab():
    for name, src in LAB_SOURCES.items():
        if name != "colab_io.py":
            assert "google.colab" not in src, name


def test_embedded_audio_only_in_player_fallback():
    for name, src in LAB_SOURCES.items():
        if name != "player.py":
            assert "display import Audio" not in src and "display.Audio" not in src, name


def test_notebook_is_current():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_notebook", ROOT / "scripts" / "build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    expected = [c["source"] for c in [mod.cell(k, s) for k, s in mod.CELLS]]
    assert [c["source"] for c in NB["cells"]] == expected, "run: python scripts/build_notebook.py"
