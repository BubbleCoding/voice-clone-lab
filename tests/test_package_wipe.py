import zipfile

from conftest import run_experiment
from lab import clone, package, quiz, wipe


def test_teacher_zip_has_every_real_and_cloned_clip(recordings, fake_model):
    run_experiment()
    with zipfile.ZipFile(package.make_all_clips_zip()) as zf:
        names = zf.namelist()
    assert "real/NL1_echt.wav" in names and "clones/NL1_3s.wav" in names
    assert len([n for n in names if n.startswith("clones/")]) == 12


def test_wipe_removes_all_audio(recordings, fake_model, data_dir):
    run_experiment()
    quiz.prepare()
    assert any(data_dir.rglob("*.wav"))
    wipe.wipe_data()
    assert not data_dir.exists()
    assert clone.MODEL is None
