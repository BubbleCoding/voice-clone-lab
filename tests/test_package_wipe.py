import zipfile

import pytest
import soundfile as sf

from conftest import run_experiment
from lab import clone, package, state, wipe
from lab.state import LabError


def test_zip_has_real_and_three_clones_at_24k(recordings, fake_model):
    with pytest.raises(LabError):
        package.make_zip()  # no clones yet
    run_experiment()
    path = package.make_zip()
    assert path.name == "K7QM-A.zip"
    with zipfile.ZipFile(path) as zf:
        assert sorted(zf.namelist()) == sorted(package.ZIP_NAMES)
    for name in package.ZIP_NAMES:
        info = sf.info(state.subdir("test") / name)
        assert info.samplerate == 24000 and info.channels == 1


def test_wipe_removes_all_audio(recordings, fake_model, data_dir):
    run_experiment()
    package.make_zip()
    assert any(data_dir.rglob("*.wav"))
    wipe.wipe_data()
    assert not data_dir.exists()
    assert clone.MODEL is None
