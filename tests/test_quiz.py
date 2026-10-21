import pytest
import soundfile as sf

from conftest import run_cell, run_experiment
from lab import audio, quiz, state
from lab.state import LabError


def test_quiz_needs_clones(recordings):
    with pytest.raises(LabError):
        quiz.prepare()


def test_quiz_shuffles_real_and_clones_into_numbered_fair_clips(recordings, fake_model):
    run_experiment()
    clips = quiz.prepare(seed=1)
    assert [c["nr"] for c in clips] == [1, 2, 3, 4]
    assert sorted(c["label"] for c in clips) == ["echt", "kloon uit 10 s", "kloon uit 3 s", "kloon uit 6 s"]
    assert sum(c["real"] for c in clips) == 1
    for c in clips:
        assert c["path"].name == f"{c['nr']}.wav"  # the filename gives nothing away
        assert sf.info(c["path"]).samplerate == audio.SR
    orders = {tuple(c["label"] for c in quiz.prepare(seed=s)) for s in range(10)}
    assert len(orders) > 1
    assert len(list(state.subdir("quiz").glob("*.wav"))) == 4  # reshuffling replaces the old files


def test_quiz_follows_custom_ref_lengths(recordings, fake_model):
    run_cell("REF_LENGTHS = [3, 6, 10]", replace={"REF_LENGTHS = [3, 6, 10]": "REF_LENGTHS = [1, 2]"})
    assert sorted(c["label"] for c in quiz.prepare()) == ["echt", "kloon uit 1 s", "kloon uit 2 s"]


def test_quiz_ignores_free_mode_clips(recordings, fake_model):
    run_experiment()
    run_cell("TEXT = ")
    assert len(quiz.prepare()) == 4


def test_quiz_cell_reveals_after_a_guess(recordings, fake_model, monkeypatch):
    import IPython.display
    from lab import cells
    shown = []
    monkeypatch.setattr(IPython.display, "display", lambda *objs: shown.extend(objs))
    run_experiment()
    cells.quiz()
    box = shown[-1]
    buttons = box.children[0].children
    assert len(buttons) == 4
    buttons[0].click()
    assert all(b.disabled for b in buttons)
    html = "".join(getattr(o, "data", "") for o in shown if hasattr(o, "data"))
    assert "is echt" in html and "kloon uit 10 s" in html
